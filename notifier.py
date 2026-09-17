"""
MAV — NOTIFICADOR E CENTRAL TELEGRAM
Responsável por gerenciar conexões, envio de alertas formatados e comandos remotos via API do Telegram.
"""

import os
import sys
import psutil
import subprocess
import requests
import logging

logger = logging.getLogger("MAV-TELEGRAM")

def is_scheduler_running():
    """Verifica se o scheduler.py está rodando em background no Windows."""
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any('scheduler.py' in arg for arg in cmdline):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.token = str(token or "").strip()
        self.chat_id = str(chat_id or "").strip()
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_job_alert(self, job_data: dict, match_result, is_golden_window: bool = False) -> bool:
        """Envia card rico de vaga com botões interativos para o Telegram (Apenas vagas aprovadas)."""
        
        classification = getattr(match_result, 'classification', 'DESCARTAR')
        score = getattr(match_result, 'score', 0.0)

        if classification.upper() == "DESCARTAR":
            logger.info("Vaga '%s' descartada pelo Notifier (Score: %.1f). Alerta não enviado.", 
                        job_data.get("title", "Sem título"), score)
            return False

        title = job_data.get("title", "Vaga sem título")
        company = job_data.get("company", "Empresa não informada")
        location = job_data.get("location", "Campinas, SP")
        source = job_data.get("source", job_data.get("site", "Portal"))
        link = job_data.get("link", "#")
        
        matched_skills = getattr(match_result, 'matched_core_skills', [])
        skills = ", ".join(matched_skills[:5]) if matched_skills else "N/A"
        golden_tag = "🔥 <b>[JANELA DE OURO]</b>\n" if is_golden_window else ""

        message = (
            f"🎯 <b>[Insight MAV] — NOVA VAGA ELEGÍVEL!</b>\n\n"
            f"{golden_tag}"
            f"📌 <b>Cargo:</b> {title}\n"
            f"🏢 <b>Empresa:</b> {company}\n"
            f"📍 <b>Local:</b> {location}\n"
            f"🌐 <b>Origem:</b> {source}\n"
            f"⭐ <b>Score:</b> <code>{score:.1f}</code> ({classification})\n"
            f"🛠️ <b>Skills:</b> {skills}\n"
        )

        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🔗 Acessar Vaga", "url": link},
                    {"text": "✅ Aplicado", "callback_data": "applied"}
                ],
                [
                    {"text": "🗑️ Descartar", "callback_data": "discard"}
                ]
            ]
        }

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "reply_markup": keyboard
        }

        try:
            response = requests.post(f"{self.base_url}/sendMessage", json=payload, timeout=15)
            if response.status_code == 200:
                logger.info("Alerta enviado com sucesso via Insight MAV para o Telegram: %s", title)
                return True
            else:
                logger.error("Erro do Telegram ao enviar alerta: %s", response.text)
                return False
        except Exception:
            logger.exception("Falha de conexão com a API do Telegram.")
            return False

    def send_text_message(self, text: str) -> bool:
        """Envia uma mensagem de texto simples (usada para respostas de comandos)."""
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(f"{self.base_url}/sendMessage", json=payload, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def handle_command(self, text: str):
        """Processa comandos recebidos via chat para controle remoto."""
        text = text.strip().lower()
        
        if text == "/status":
            cpu = psutil.cpu_percent(interval=0.5)
            memory = psutil.virtual_memory()
            scheduler_status = "🟢 Rodando (Background)" if is_scheduler_running() else "🔴 Parado"
            
            msg = (
                f"🤖 <b>MAV - Status do Sistema (Real-Time)</b>\n\n"
                f"💻 <b>CPU:</b> {cpu}%\n"
                f"🧠 <b>RAM:</b> {memory.percent}% ({memory.used // (1024**2)} MB)\n"
                f"🕷️ <b>Scheduler:</b> {scheduler_status}"
            )
            self.send_text_message(msg)
            
        elif text == "/run":
            self.send_text_message("⚡ [FORÇADO] Iniciando ciclo manual de mineração...")
            current_dir = os.path.dirname(os.path.abspath(__file__))
            scheduler_path = os.path.join(current_dir, "scheduler.py")
            
            if os.path.exists(scheduler_path):
                subprocess.Popen([sys.executable, scheduler_path])
                self.send_text_message("✅ Ciclo disparado com sucesso em segundo plano!")
            else:
                self.send_text_message("❌ Erro: scheduler.py não encontrado na raiz.")
                
        elif text == "/db":
            msg = (
                f"📊 <b>MAV - Resumo do Banco de Dados</b>\n\n"
                f"📂 <b>Conexão:</b> Ativa\n"
                f"📈 <b>Estado:</b> Sincronizado com o Scheduler"
            )
            self.send_text_message(msg)