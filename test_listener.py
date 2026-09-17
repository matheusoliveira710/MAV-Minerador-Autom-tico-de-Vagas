import os
import json
from pathlib import Path
import time
import requests

BASE_DIR = Path(__file__).resolve().parent

# Credenciais fixas para teste imediato
token = "8814651743:AAFRcCTE563aEJ4wmsaMfd2Vi6zOtz_Onr4"
chat_id = "1348774750"

# (Opcional) Se quiser tentar ler do config.json mantendo as credenciais fixas como fallback:
config_path = BASE_DIR / "config.json"
if config_path.exists():
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            token = cfg.get("TELEGRAM_BOT_TOKEN") or cfg.get("token") or token
            chat_id = cfg.get("TELEGRAM_CHAT_ID") or cfg.get("chat_id") or chat_id
    except Exception as e:
        print(f"[AVISO] Falha ao ler config.json, usando valores padrão: {e}")

print(f"[TESTE] Token carregado: {token[:6]}...")
print(f"[TESTE] Chat ID carregado: {chat_id}")
print("[TESTE] Ouvindo mensagens... Mande '/status' ou '/rodar' no seu Telegram agora!")

offset = 0
offset = 0
while True:
    try:
        url = f"https://api.telegram.org/bot{token}/getUpdates?offset={offset}&timeout=30"
        res = requests.get(url, timeout=35).json()
        
        if not res.get("ok"):
            time.sleep(2)
            continue
            
        for update in res.get("result", []):
            offset = update["update_id"] + 1
            msg = update.get("message", {})
            text = msg.get("text", "").strip()
            sender_id = str(msg.get("chat", {}).get("id", ""))
            
            print(f"[MENSAGEM RECEBIDA] De: {sender_id} | Texto: {text}")
            
            reply_url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(reply_url, json={
                "chat_id": sender_id,
                "text": f"✅ Comando reconhecido pelo PC: *{text}*",
                "parse_mode": "Markdown"
            }, timeout=10)
            
    except requests.exceptions.RequestException:
        # Se cair a conexão ou der timeout, apenas aguarda e tenta de novo sem crashar
        time.sleep(5)
    except Exception as e:
        print(f"[ERRO INESPERADO] {e}")
        time.sleep(5)
