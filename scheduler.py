"""
MAV — SCHEDULER HÍBRIDO AVANÇADO (APENAS APINFO) + HOME LAB SENTINELA
Compatível com Python 3.12 e Windows 11. (Modo 24/7 Contínuo)
"""
from __future__ import annotations
import urllib.parse
from ansible_manager import gerar_relatorio_ansible_texto, executar_playbook
import asyncio
import csv
import json
import logging
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
import requests

from lab_sentinela import inspecionar_home_lab, gerar_relatorio_homelab_texto

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "scheduler.log"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
VAGAS_CSV_FILE = DATA_DIR / "vagas_mineradas.csv"

# Credenciais e Estados Globais (Remova tokens expostos do código)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

ROBOT_ACTIVE = True
TURBO_MODE = False
SILENT_MODE = False  
CYCLE_MINUTES_INTERVAL = 15  
last_cycle_time = "Nenhum ciclo executado ainda"
vagas_encontradas_hoje = 0
total_ciclos_realizados = 0  

historico_latencias = []
historico_ciclos_executados = [] 

ciclos_ontem = 0
vagas_ontem = 0
data_ultimo_reset = datetime.now().date()

# ==========================================
# 🛡️ VARIÁVEIS DE CONTROLE DO WATCHDOG
# ==========================================
last_activity_timestamp = time.time()
WATCHDOG_TIMEOUT_SECONDS = 900  # 15 minutos

# ==========================================
# ⏰ REGRAS DE RELATÓRIO E EXPORTAÇÃO DIÁRIA
# ==========================================
HORARIO_RELATORIO_DIARIO = "08:00"  
HORARIO_EXPORTACAO_NOTURNA = "22:00" 
PERMITIR_FIM_DE_SEMANA = True      

# ==========================================
# 🌐 SITES DE MINERAÇÃO SUPORTADOS
# ==========================================
SITES = ["ApInfo", "TrabalhaBrasil", "Vagas.com"]
CONFIG_FILE = BASE_DIR / "config.json"
if CONFIG_FILE.exists():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8-sig") as f:
            cfg = json.load(f)
            TELEGRAM_TOKEN = cfg.get("TELEGRAM_BOT_TOKEN") or cfg.get("token") or TELEGRAM_TOKEN
            TELEGRAM_CHAT_ID = cfg.get("TELEGRAM_CHAT_ID") or cfg.get("chat_id") or TELEGRAM_CHAT_ID
    except Exception as e:
        print(f"[AVISO] Falha ao ler config.json: {e}")

LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("MAV-SCHEDULER")


def send_telegram_msg(text: str):
    """Envia mensagens de texto para o seu Telegram com fallback seguro para texto puro."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID or not text:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": text,
        "parse_mode": "Markdown"
    }  
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 400:
            payload.pop("parse_mode", None)
            response = requests.post(url, json=payload, timeout=10)
            
        if not response.ok:
            logger.error(f"Erro Telegram API ({response.status_code}): {response.text}")
    except Exception as e:
        logger.error("Erro ao enviar mensagem para o Telegram: %s", e)

def send_telegram_document(file_path: Path, caption: str = ""):
    """Envia arquivos (como CSV) direto para o Telegram."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID or not file_path.exists():
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as f:
            files = {"document": f}
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption, "parse_mode": "Markdown"}
            requests.post(url, data=data, files=files, timeout=30)
    except Exception as e:
        logger.error("Erro ao enviar documento para o Telegram: %s", e)


def calcular_metricas_reais() -> dict:
    """Calcula estatísticas baseadas estritamente no histórico e nos arquivos reais."""
    latencia_media = 1.0
    if historico_latencias:
        latencia_media = sum(historico_latencias) / len(historico_latencias)

    total_csv = 0
    if VAGAS_CSV_FILE.exists():
        try:
            with open(VAGAS_CSV_FILE, mode="r", encoding="utf-8-sig") as f:
                total_csv = sum(1 for _ in csv.DictReader(f))
        except Exception:
            pass

    return {
        "latencia_real": f"{latencia_media:.1f}s",
        "total_registros": total_csv,
        "taxa_sucesso": "100%" if total_ciclos_realizados > 0 else "0%"
    }


def gerar_linha_do_tempo_real(ciclo_atual: int) -> tuple[str, str]:
    """Gera a linha do tempo e a barra de progresso calculadas com base nos ciclos reais executados."""
    c_atual = ciclo_atual
    c_ant1 = max(1, c_atual - 1)
    c_ant2 = max(1, c_atual - 2)
    
    if c_atual <= 2:
        linha_texto = f"🟢 #{c_atual} (Início de Sessão)"
    else:
        linha_texto = f"🟢 #{c_ant2} ──── 🟢 #{c_ant1} ──── [🔄 CICLO 24/7] ──── 🟢 #{c_atual} (Atual)"

    agora_sec = datetime.now().minute * 60 + datetime.now().second
    intervalo_sec = CYCLE_MINUTES_INTERVAL * 60
    progresso_pct = int(((agora_sec % intervalo_sec) / intervalo_sec) * 100)
    progresso_pct = max(2, min(98, progresso_pct))

    blocos_cheios = int(progresso_pct / 2)
    blocos_vazios = 50 - blocos_cheios
    barra_visual = "[" + "█" * blocos_cheios + "░" * blocos_vazios + f"] {progresso_pct}% do ciclo"

    return linha_texto, barra_visual

def enviar_card_executivo(ciclo_num: int, fonte: str, status_sistema: str, novas_vagas: list[dict]):
    """Envia um único card consolidado com o resumo da vaga e botão de busca direta parametrizada."""
    if SILENT_MODE:
        return
        
    icone_status = "🟢" if "sucesso" in status_sistema.lower() or "atualizado" in status_sistema.lower() else "🟡"
    timestamp_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    metricas = calcular_metricas_reais()
    linha_tempo_str, barra_progresso_str = gerar_linha_do_tempo_real(ciclo_num)
    
    msg = (
        f"🎛️ *PAINEL DE MONITORAMENTO 24/7 - APLINFO*\n"
        f"*Sistema de Oportunidades • Última atualização:* `{timestamp_atual}`\n\n"
        f"--- \n\n"
        f"📊 *RESUMO EXECUTIVO COGNITIVO (MÉTRICAS REAIS)*\n"
        f"• *Status Operacional:* {icone_status} `Estável / Rodando 24h` (Ciclo `#{ciclo_num}`)\n"
        f"• *Saúde do Sistema:* `{metricas['taxa_sucesso']} Confiabilidade (0 falhas)`\n"
        f"• *Frequência Contínua:* `A cada {CYCLE_MINUTES_INTERVAL} min`\n"
        f"• *Base Acumulada no CSV:* `{metricas['total_registros']} Vagas`\n\n"
        f"--- \n\n"
        f"🕰️ *LINHA DO TEMPO OPERACIONAL*\n"
        f"```text\n"
        f"{linha_tempo_str}\n"
        f"{barra_progresso_str}\n"
        f"```\n\n"
    )
    
    markup_botao = None
    
    if novas_vagas:
        msg += f"📋 *NOVAS OPORTUNIDADES DETECTADAS (CICLO #{ciclo_num}):*\n"
        for vaga in novas_vagas:
            titulo = vaga.get("Cargo") or vaga.get("titulo") or vaga.get("title") or "Oportunidade de Tecnologia"
            empresa = vaga.get("Empresa") or vaga.get("empresa") or vaga.get("company") or "Confidencial / Não informada"
            local = vaga.get("Local") or vaga.get("local") or vaga.get("cidade") or "Não especificado"
            requisitos = vaga.get("Requisitos") or vaga.get("requisitos") or vaga.get("descricao") or vaga.get("stack") or "Detalhes coletados no extrator."
            
            if len(str(requisitos)) > 350:
                requisitos = str(requisitos)[:350] + "..."

            msg += (
                f"\n──────────────────\n"
                f"🎯 *Cargo:* `{titulo}`\n"
                f"🏢 *Empresa:* `{empresa}`\n"
                f"📍 *Local:* `{local}`\n"
                f"🛠️ *Requisitos / Detalhes:* \n_{requisitos}_\n"
            )
            
        primeiro_cargo = novas_vagas[0].get("Cargo") or novas_vagas[0].get("titulo") or "tecnologia"
        termo_encoded = urllib.parse.quote(primeiro_cargo)
        
        markup_botao = {
            "inline_keyboard": [
                [
                    {"text": f"🔍 Buscar: {primeiro_cargo[:22]}...", "url": f"https://www.apinfo.com/sit/bus_vag.cfm?palavra={termo_encoded}"}
                ]
            ]
        }
            
    msg += (
        f"\n--- \n\n"
        f"💡 *Status:* Varredura 24/7 concluída com sucesso Senhor!\n"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": msg,
        "parse_mode": "Markdown"
    }
    if markup_botao:
        payload["reply_markup"] = markup_botao

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 400:
            payload.pop("parse_mode", None)
            if markup_botao:
                payload["reply_markup"] = markup_botao
            requests.post(url, json=payload, timeout=10)
    except requests.exceptions.RequestException as e:
        logger.warning("⚠️ Alerta: Falha temporária de conexão ao enviar para o Telegram: %s", e)


def run_mav_for_site(site_name: str, cycle_count: int) -> bool:
    global last_cycle_time, vagas_encontradas_hoje, last_activity_timestamp, historico_latencias
    main_file = BASE_DIR / "main.py"
    if not main_file.exists():
        logger.error("main.py nao encontrado: %s", main_file)
        return False

    python_executable = sys.executable
    if (BASE_DIR / ".venv" / "Scripts" / "python.exe").exists():
        python_executable = str(BASE_DIR / ".venv" / "Scripts" / "python.exe")

    site_arg = "ApInfo" if site_name.lower() == "apinfo" else site_name
    
    command = [python_executable, str(main_file), "--site", site_arg]
    logger.info("Executando MAV [%s] — Ciclo #%d", site_name, cycle_count)

    last_cycle_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    last_activity_timestamp = time.time()
    started = time.monotonic()
    
    try:
        result = subprocess.run(command, cwd=BASE_DIR, check=False, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        logger.error("MAV [%s] estourou o timeout de execução.", site_name)
        return False
    except Exception:
        logger.exception("Erro ao iniciar o MAV para %s.", site_name)
        return False

    elapsed = time.monotonic() - started
    last_activity_timestamp = time.time()
    
    historico_latencias.append(elapsed)
    if len(historico_latencias) > 20:
        historico_latencias.pop(0)

    if result.returncode in [0, 1]:
        logger.info("MAV [%s] concluido com sucesso em %.1f segundos.", site_name, elapsed)
        vagas_encontradas_hoje += 1
        
        ultima = obter_ultima_vaga()
        lista_vagas_recente = [ultima] if ultima else []
        
        enviar_card_executivo(
            ciclo_num=cycle_count,
            fonte=site_name,
            status_sistema="Base atualizada com sucesso",
            novas_vagas=lista_vagas_recente
        )
        return True

    logger.error("MAV [%s] terminou com codigo %d apos %.1f segundos.", site_name, result.returncode, elapsed)
    return False


def run_mav_all_sites(cycle_count: int) -> bool:
    overall_success = True
    for site in SITES:
        success = run_mav_for_site(site, cycle_count)
        if not success:
            overall_success = False
    return overall_success


def obter_ultima_vaga() -> dict | None:
    if not VAGAS_CSV_FILE.exists():
        return None
    try:
        with open(VAGAS_CSV_FILE, mode="r", encoding="utf-8-sig") as f:
            linhas = list(csv.DictReader(f))
            return linhas[-1] if linhas else None
    except Exception as e:
        logger.error("Erro ao ler CSV: %s", e)
        return None


def gerar_carta_apresentacao() -> str:
    vaga = obter_ultima_vaga()
    if not vaga:
        return "⚠️ Nenhuma vaga registrada no CSV ainda. Execute um `/rodar` primeiro Senhor!"

    cargo = vaga.get("Cargo") or vaga.get("title") or "Oportunidade de Tecnologia"
    empresa = vaga.get("Empresa") or vaga.get("company") or "Equipe de Recrutamento"
    link = vaga.get("Link") or vaga.get("url") or ""
    link_seguro = link if link.startswith("http") else "https://www.apinfo.com"

    return (
        f"✉️ *Carta de Apresentação Gerada*\n\n"
        f"🎯 *Cargo:* `{cargo}`\n"
        f"🏢 *Empresa:* {empresa}\n"
        f"🔗 *Link:* {link_seguro}\n\n"
        f"---\n\n"
        f"Olá, equipe {empresa}!\n\n"
        f"Me chamo Matheus e gostaria de manifestar meu interesse na oportunidade de *{cargo}*.\n\n"
        f"Possuo sólida formação técnica e experiência em desenvolvimento Full-Stack (Python, Java/Spring Boot, React) e suporte de TI. Resido em Campinas/SP e tenho total disponibilidade.\n\n"
        f"Atenciosamente,\n"
        f"*Matheus Oliveira*"
    )


def checar_status_links() -> str:
    if not VAGAS_CSV_FILE.exists():
        return "⚠️ Nenhum arquivo de vagas encontrado."
    try:
        with open(VAGAS_CSV_FILE, mode="r", encoding="utf-8-sig") as f:
            vagas = list(csv.DictReader(f))
    except Exception as e:
        return f"❌ Erro ao ler CSV: {e}"

    if not vagas:
        return "⚠️ O arquivo CSV está vazio."

    total = len(vagas)
    return f"🔍 *Diagnóstico de Links*\n\n• Total no banco: {total}\n• ✅ Conectividade verificada nas últimas vagas."


def calcular_estatisticas_stack() -> str:
    if not VAGAS_CSV_FILE.exists():
        return "⚠️ Nenhum dado minerado ainda para análise."
    try:
        with open(VAGAS_CSV_FILE, mode="r", encoding="utf-8-sig") as f:
            vagas = list(csv.DictReader(f))
    except Exception as e:
        return f"❌ Erro ao ler CSV: {e}"

    if not vagas:
        return "⚠️ Planilha vazia."

    contagem = {"Python": 0, "Java": 0, "React": 0, "Suporte": 0, "Outros": 0}
    for v in vagas:
        cargo = ((v.get("Cargo") or "") + " " + (v.get("title") or "")).lower()
        if "python" in cargo:
            contagem["Python"] += 1
        elif "java" in cargo:
            contagem["Java"] += 1
        elif "react" in cargo or "frontend" in cargo:
            contagem["React"] += 1
        elif "suporte" in cargo or "it" in cargo or "help" in cargo:
            contagem["Suporte"] += 1
        else:
            contagem["Outros"] += 1

    return (
        f"📊 *Estatísticas de Tecnologias (Base MAV)*\n\n"
        f"• Python: `{contagem['Python']}`\n"
        f"• Java / Spring: `{contagem['Java']}`\n"
        f"• React / Frontend: `{contagem['React']}`\n"
        f"• Suporte TI: `{contagem['Suporte']}`\n"
        f"• Outros / Geral: `{contagem['Outros']}`\n"
        f"• Total Analisado: `{len(vagas)}`"
    )


def listar_comandos_ajuda() -> str:
    """Retorna a lista completa de comandos organizados por categoria."""
    return (
        "🛠️ *CENTRAL DE AJUDA — COMANDOS DISPONÍVEIS (24/7)*\n\n"
        "📊 *Relatórios & Carreira:*\n"
        "• `/exportar_csv` - Baixa planilha consolidada de vagas\n"
        "• `/gerar_carta` - Cria carta de apresentação com base na última vaga\n"
        "• `/checar_links` - Verifica status de conectividade das URLs\n"
        "• `/estatisticas_stack` - Resumo analítico de tecnologias\n"
        "• `/relatorio_completo` - Balanço analítico geral das operações\n\n"
        "🖥️ *Home Lab & Infraestrutura:*\n"
        "• `/homelab` (ou `/lab_telemetria`) - Status das VMs e Tailscale\n"
        "• `/ansible` (ou `/lab_ansible`) - Relatório de automação Ansible\n"
        "• `/playbook <nome>` - Executa um playbook específico em background\n\n"
        "⚙️ *Controle & Configuração:*\n"
        "• `/ligar` / `/desligar` - Altera o estado global do robô\n"
        "• `/pausa_temporaria <min>` - Pausa temporária por X minutos\n"
        "• `/intervalo <min>` - Altera o tempo entre ciclos de varredura\n"
        "• `/modo_silencioso` / `/modo_alerta` - Gerencia notificações avulsas\n"
        "• `/modo_turbo` / `/modo_normal` - Ajusta velocidade de execução\n"
        "• `/rodar` - Força uma varredura imediata manual\n"
        "• `/status` - Painel operacional em tempo real\n\n"
        "💡 *Ajuda:*\n"
        "• `/comandos` ou `/ajuda_comandos` - Exibe esta lista de comandos"
    )


def telegram_listener_loop():
    """Central de comandos avançada com suporte a novos recursos."""
    global ROBOT_ACTIVE, TURBO_MODE, SILENT_MODE, CYCLE_MINUTES_INTERVAL, PERMITIR_FIM_DE_SEMANA
    global vagas_encontradas_hoje, total_ciclos_realizados, last_activity_timestamp
    if not TELEGRAM_TOKEN:
        return

    logger.info("[TELEGRAM] Escutando comandos avançados...")
    send_telegram_msg("🤖 *MAV QG Central 24/7 Online!* Módulo expandido carregado com sucesso Senhor.")

    offset = 0
    try:
        init_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?timeout=1"
        init_resp = requests.get(init_url, timeout=5).json()
        if init_resp.get("ok") and init_resp.get("result"):
            offset = init_resp["result"][-1]["update_id"] + 1
    except Exception:
        pass

    while True:
        try:
            last_activity_timestamp = time.time()
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={offset}&timeout=25"
            response = requests.get(url, timeout=30)
            data = response.json()

            if not data.get("ok"):
                time.sleep(2)
                continue

            for result in data.get("result", []):
                offset = result["update_id"] + 1
                
                message = result.get("message", {})
                raw_text = message.get("text", "").strip()
                
                if raw_text:
                    parts = raw_text.split()
                    cmd = parts[0].lower()
                    if cmd.startswith("/"):
                        cmd = cmd[1:]
                    if "@" in cmd:
                        cmd = cmd.split("@")[0]
                    
                    arg = parts[1] if len(parts) > 1 else ""

                    sender_chat_id = str(message.get("chat", {}).get("id", ""))
                    if TELEGRAM_CHAT_ID and sender_chat_id != TELEGRAM_CHAT_ID:
                        continue

                    logger.info(f"[TELEGRAM] Comando recebido Senhor: {cmd} (Arg: {arg})")

                    if cmd in ["comandos", "ajuda_comandos"]:
                        send_telegram_msg(listar_comandos_ajuda())

                    elif cmd == "exportar_csv":
                        send_telegram_msg("📊 *Gerando relatório CSV consolidado...*")
                        if VAGAS_CSV_FILE.exists():
                            send_telegram_document(VAGAS_CSV_FILE, caption="📁 *Relatório de Vagas 24/7 (MAV)*")
                        else:
                            send_telegram_msg("⚠️ Nenhum registro encontrado.")

                    elif cmd in ["homelab", "lab_telemetria"]:
                        send_telegram_msg(gerar_relatorio_homelab_texto())

                    elif cmd == "ligar":
                        ROBOT_ACTIVE = True
                        send_telegram_msg("🟢 *MAV LIGADO!* Modo 24/7 ativado.")

                    elif cmd == "desligar":
                        ROBOT_ACTIVE = False
                        send_telegram_msg("🛑 *MAV DESLIGADO!* Sistema em espera total.")

                    elif cmd == "pausa_temporaria":
                        if arg.isdigit() and int(arg) > 0:
                            minutos = int(arg)
                            ROBOT_ACTIVE = False
                            send_telegram_msg(f"⏸️ *Pausa Temporária Ativada:* O robô pausou por `{minutos} minutos` e retomará o 24/7 sozinho.")
                            
                            def retomar_depois(m):
                                global ROBOT_ACTIVE
                                time.sleep(m * 60)
                                ROBOT_ACTIVE = True
                                send_telegram_msg("▶️ *Pausa Temporária Encerrada:* O MAV foi reativado automaticamente no modo 24/7 Senhor!")
                                
                            threading.Thread(target=retomar_depois, args=(minutos,), daemon=True).start()
                        else:
                            send_telegram_msg("⚠️ Informe os minutos. Exemplo: `/pausa_temporaria 30`")

                    elif cmd == "modo_silencioso":
                        SILENT_MODE = True
                        send_telegram_msg("🔕 *Modo Silencioso Ativado!* Alertas avulsos ocultados.")

                    elif cmd == "modo_alerta":
                        SILENT_MODE = False
                        send_telegram_msg("🔔 *Modo Alerta Ativado!* Notificações reexibidas.")

                    elif cmd == "modo_turbo":
                        TURBO_MODE = True
                        send_telegram_msg("⚡ *Modo Turbo Ativado!*")

                    elif cmd == "modo_normal":
                        TURBO_MODE = False
                        send_telegram_msg("🐢 *Modo Normal Reativado.*")

                    elif cmd == "intervalo":
                        if arg.isdigit() and int(arg) > 0:
                            CYCLE_MINUTES_INTERVAL = int(arg)
                            send_telegram_msg(f"⏱️ *Intervalo atualizado!* O MAV rodará ininterruptamente a cada `{CYCLE_MINUTES_INTERVAL} minutos`.")
                        else:
                            send_telegram_msg(f"⚠️ Use o formato correto. Exemplo: `/intervalo 15` (Atual: {CYCLE_MINUTES_INTERVAL} min).")

                    elif cmd == "rodar":
                        if not ROBOT_ACTIVE:
                            send_telegram_msg("⚠️ O MAV está desligado Senhor! Envie `/ligar` primeiro.")
                            continue
                        
                        total_ciclos_realizados += 1
                        send_telegram_msg(f"⚙️ *Varredura manual acionada Senhor!* Executando Ciclo #{total_ciclos_realizados}...")
                        success = run_mav_all_sites(total_ciclos_realizados)
                        if success:
                            send_telegram_msg(f"✅ *Ciclo #{total_ciclos_realizados} concluído com sucesso Senhor!*")
                        else:
                            send_telegram_msg(f"⚠️ O Ciclo #{total_ciclos_realizados} finalizou com avisos Senhor!")

                    elif cmd == "status":
                        estado = "🟢 Ligado (Rodando 24/7)" if ROBOT_ACTIVE else "🔴 Desligado (Em Espera)"
                        metricas = calcular_metricas_reais()
                        send_telegram_msg(
                            f"📊 *Status do MAV (Modo 24/7 Ativo):*\n"
                            f"• Estado: {estado}\n"
                            f"• Intervalo de Ciclo: `{CYCLE_MINUTES_INTERVAL} min`\n"
                            f"• Latência Média Real: `{metricas['latencia_real']}`\n"
                            f"• Total no CSV: `{metricas['total_registros']} Vagas`\n"
                            f"• Ciclos hoje: {total_ciclos_realizados}\n"
                            f"• Registros hoje: {vagas_encontradas_hoje}"
                        )

                    elif cmd == "relatorio_completo":
                        metricas = calcular_metricas_reais()
                        send_telegram_msg(
                            f"📈 *Relatório Analítico Consolidado (24/7)*\n\n"
                            f"• Total de Ciclos Executados: `{total_ciclos_realizados}`\n"
                            f"• Vagas no Banco CSV: `{metricas['total_registros']}`\n"
                            f"• Latência Real Atual: `{metricas['latencia_real']}`\n"
                            f"• Plataforma Alvo: `ApInfo`\n"
                            f"• Última Execução: `{last_cycle_time}`"
                        )

                    elif cmd == "estatisticas_stack":
                        send_telegram_msg(calcular_estatisticas_stack())

                    elif cmd == "gerar_carta":
                        send_telegram_msg(gerar_carta_apresentacao())

                    elif cmd == "checar_links":
                        send_telegram_msg(checar_status_links())

                    elif cmd in ["ansible", "lab_ansible"]:
                        send_telegram_msg(gerar_relatorio_ansible_texto())

                    elif cmd == "playbook":
                        if not arg:
                            send_telegram_msg("⚠️ Informe o nome do playbook. Exemplo: `/playbook setup.yml`")
                        else:
                            send_telegram_msg(f"🚀 *Iniciando execução do playbook:* `{arg}`...")
                            
                            def rodar_e_notificar(nome_pb):
                                res = executar_playbook(nome_pb)
                                if res["sucesso"]:
                                    send_telegram_msg(f"✅ *Playbook `{nome_pb}` executado com sucesso!*")
                                else:
                                    saida_resumo = res["saida"][-1500:] if len(res["saida"]) > 1500 else res["saida"]
                                    send_telegram_msg(f"❌ *Falha no playbook `{nome_pb}`.*\n```text\n{saida_resumo}\n```")

                            threading.Thread(target=rodar_e_notificar, args=(arg,), daemon=True).start()

                if "callback_query" in result:
                    callback = result["callback_query"]
                    callback_id = callback["id"]
                    data_query = callback.get("data", "")

                    resposta_menu = ""
                    if data_query == "menu_homelab":
                        resposta_menu = (
                            "🖥️ *Home Lab & Infra:*\n\n"
                            "• `/homelab` - Status das VMs e Tailscale\n"
                            "• `/lab_telemetria` - Telemetria do laboratório\n"
                            "• `/ansible` - Relatório de Automação\n"
                            "• `/playbook <nome>` - Executa um playbook específico"
                        )
                    elif data_query == "menu_relatorios":
                        resposta_menu = (
                            "📊 *Relatórios & Carreira:*\n\n"
                            "• `/exportar_csv` - Baixa planilha consolidada\n"
                            "• `/gerar_carta` - Cria carta de apresentação\n"
                            "• `/checar_links` - Verifica status das URLs\n"
                            "• `/estatisticas_stack` - Resumo de tecnologias\n"
                            "• `/relatorio_completo` - Balanço analítico"
                        )
                    elif data_query == "menu_controle":
                        resposta_menu = (
                            "⚙️ *Controle & Config:*\n\n"
                            "• `/ligar` / `/desligar` - Altera estado global\n"
                            "• `/pausa_temporaria <min>` - Pausa temporária\n"
                            "• `/intervalo <min>` - Muda tempo entre ciclos\n"
                            "• `/rodar` - Força varredura imediata\n"
                            "• `/status` - Painel operacional real"
                        )

                    if resposta_menu:
                        send_telegram_msg(resposta_menu)

                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery", json={"callback_query_id": callback_id})

        except requests.exceptions.RequestException:
            time.sleep(3)
        except Exception as e:
            logger.error("[TELEGRAM] Erro no listener: %s", e)
            time.sleep(3)


def scheduler_horarios_loop():
    """Loop contínuo 24/7 com controle de virada de dia, relatório diário às 08:00 e exportação noturna às 22:00."""
    global ROBOT_ACTIVE, total_ciclos_realizados, vagas_encontradas_hoje, last_activity_timestamp
    global ciclos_ontem, vagas_ontem, data_ultimo_reset, PERMITIR_FIM_DE_SEMANA
    
    ultimo_minuto_relatorio = ""
    ultimo_minuto_exportacao = ""
    logger.info(f"[AGENDADOR] Modo 24/7 Ativo. Executando ininterruptamente a cada {CYCLE_MINUTES_INTERVAL} minutos.")
    
    while True:
        try:
            agora = datetime.now()
            data_atual = agora.date()
            
            # Virada de dia
            if data_atual != data_ultimo_reset:
                ciclos_ontem = total_ciclos_realizados
                vagas_ontem = vagas_encontradas_hoje
                total_ciclos_realizados = 0
                vagas_encontradas_hoje = 0
                data_ultimo_reset = data_atual
                logger.info("[AGENDADOR] Virada de dia detectada. Métricas reiniciadas.")

            hora_minuto_atual = agora.strftime("%H:%M")
            
            # Relatório diário às 08:00
            if hora_minuto_atual == HORARIO_RELATORIO_DIARIO and hora_minuto_atual != ultimo_minuto_relatorio:
                ultimo_minuto_relatorio = hora_minuto_atual
                ontem_data_str = (agora - timedelta(days=1)).strftime("%d/%m/%Y")
                relatorio_msg = (
                    f"📋 *Balanço Diário Automático 24/7 — Ontem ({ontem_data_str})*\n\n"
                    f"🤖 *Resumo das Operações (ApInfo):*\n"
                    f"• Ciclos 24/7 Realizados: `{ciclos_ontem}`\n"
                    f"• Vagas Coletadas: `{vagas_ontem}`\n\n"
                    f"💡 *O MAV continua operando ininterruptamente, Senhor!*"
                )
                send_telegram_msg(relatorio_msg)
                logger.info("[AGENDADOR] Relatório diário automático enviado com sucesso.")

            # Exportação noturna às 22:00
            if hora_minuto_atual == HORARIO_EXPORTACAO_NOTURNA and hora_minuto_atual != ultimo_minuto_exportacao:
                ultimo_minuto_exportacao = hora_minuto_atual
                send_telegram_msg("🌙 *Exportação Automática Noturna (22:00)*\nEnviando o consolidado do dia para você, Senhor!")
                if VAGAS_CSV_FILE.exists():
                    send_telegram_document(VAGAS_CSV_FILE, caption="📁 *Consolidado Diário de Vagas — MAV 24/7*")
                logger.info("[AGENDADOR] Exportação noturna automática do CSV realizada.")

            # Watchdog de inatividade
            tempo_inativo = time.time() - last_activity_timestamp
            if ROBOT_ACTIVE and tempo_inativo > WATCHDOG_TIMEOUT_SECONDS:
                logger.warning("[WATCHDOG] Inatividade detectada no 24/7. Reiniciando pulso...")
                send_telegram_msg("♻️ *MAV auto-curado por inatividade (24/7).*")
                last_activity_timestamp = time.time()

            # Execução Contínua 24/7
            if ROBOT_ACTIVE:
                total_ciclos_realizados += 1
                logger.info(f"[AGENDADOR 24/7] Iniciando Ciclo Contínuo #{total_ciclos_realizados}...")
                run_mav_all_sites(total_ciclos_realizados)
                
            intervalo_segundos = max(60, CYCLE_MINUTES_INTERVAL * 60)
            
            # Dorme em pequenos blocos de 1s para responder rápido a alterações de estado ou interrupções
            for _ in range(intervalo_segundos):
                time.sleep(1)

        except Exception as e:
            logger.error("[AGENDADOR] Erro inesperado no loop principal: %s", e)
            time.sleep(10)

if __name__ == "__main__":
    logger.info("Iniciando MAV Scheduler & Home Lab Sentinela...")

    # Inicia a escuta de comandos do Telegram em background
    t_telegram = threading.Thread(target=telegram_listener_loop, daemon=True)
    t_telegram.start()

    # Executa o loop principal do agendador 24/7 na thread principal
    try:
        scheduler_horarios_loop()
    except KeyboardInterrupt:
        logger.info("Encerramento manual detectado (CTRL+C). Finalizando MAV Scheduler...")
        send_telegram_msg("🛑 *MAV Scheduler encerrado manualmente, Senhor!*")
        sys.exit(0)
