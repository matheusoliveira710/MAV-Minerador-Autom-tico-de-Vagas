import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import requests

BASE_DIR = Path(__file__).resolve().parent
PROFILE_FILE = BASE_DIR / "data" / "profile.json"
SCREENSHOT_DIR = BASE_DIR / "data" / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

def carregar_perfil():
    if not PROFILE_FILE.exists():
        raise FileNotFoundError("Arquivo profile.json não encontrado na pasta data/!")
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def enviar_foto_com_botoes(chat_token, chat_id, foto_path, caption):
    """Envia a captura de tela para o Telegram com botões interativos de aprovação."""
    url = f"https://api.telegram.org/bot{chat_token}/sendPhoto"
    
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Enviar Agora", "callback_data": "apply_yes"},
                {"text": "❌ Cancelar", "callback_data": "apply_no"}
            ]
        ]
    }
    
    with open(foto_path, "rb") as photo:
        files = {"photo": photo}
        data = {
            "chat_id": chat_id,
            "caption": caption,
            "reply_markup": json.dumps(keyboard)
        }
        response = requests.post(url, data=data, files=files, timeout=30)
        return response.json()

def run_auto_apply(vaga_url: str, cargo: str, empresa: str, telegram_token: str, chat_id: str):
    """Executa a automação até a etapa anterior ao clique final de envio."""
    perfil = carregar_perfil()
    
    with sync_playwright() as p:
        # headless=False para você conseguir acompanhar o robô no navegador (pode mudar para True depois)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        
        try:
            print(f"[AUTO-APPLY] Acessando vaga: {vaga_url}")
            page.goto(vaga_url, timeout=60000)
            page.wait_for_load_state("networkidle")
            
            # Exemplo de preenchimento de campos genéricos de formulários de emprego
            # (Ajuste os seletores conforme o DOM real do ApInfo)
            try:
                if page.locator("input[name*='name']").count() > 0:
                    page.fill("input[name*='name']", perfil["nome_completo"])
                if page.locator("input[name*='email']").count() > 0:
                    page.fill("input[name*='email']", perfil["email"])
                if page.locator("input[name*='phone']").count() > 0:
                    page.fill("input[name*='phone']", perfil["telefone"])
            except Exception as e:
                print(f"[AVISO] Alguns campos do formulário não foram encontrados automaticamente: {e}")

            # Aguarda a página estabilizar após o preenchimento
            page.wait_for_timeout(2000)
            
            # Tira o print da tela de revisão da candidatura
            screenshot_path = SCREENSHOT_DIR / "candidatura_revisao.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            print("[AUTO-APPLY] Print da tela gerado com sucesso.")
            
            # Envia o desafio para o Telegram
            caption = (
                f"🛡️ *Validação de Candidatura Humana*\n\n"
                f"🎯 **Cargo:** {cargo}\n"
                f"🏢 **Empresa:** {empresa}\n\n"
                f"O MAV preencheu o formulário acima. Deseja confirmar o envio?"
            )
            
            resposta_tg = enviar_foto_com_botoes(telegram_token, chat_id, screenshot_path, caption)
            
            # Armazenamos temporariamente o contexto do browser aberto para fechá-lo via callback
            # (Em produção, o ID da mensagem do Telegram pode ser usado para mapear o processo ativo)
            return True, browser, page
            
        except Exception as e:
            print(f"[ERRO NO AUTO-APPLY]: {e}")
            browser.close()
            return False, None, None