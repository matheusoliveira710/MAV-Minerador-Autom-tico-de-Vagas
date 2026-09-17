import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# DIRETÓRIO BASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


# ============================================================
# TELEGRAM / INSIGHT MAV
# ============================================================

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "8814651743:AAFRcCTE563aEJ4wmsaMfd2Vi6zOtz_Onr4"
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "1348774750"
)


# ============================================================
# DISCORD (Legado / Opcional)
# ============================================================

DISCORD_WEBHOOK_URL = os.getenv(
    "DISCORD_WEBHOOK_URL",
    ""
)


# ============================================================
# PLAYWRIGHT
# ============================================================

HEADLESS = True

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/139.0.0.0 Safari/537.36"
)

PAGE_TIMEOUT = 30_000

MIN_DELAY = 1.5
MAX_DELAY = 3.5


# ============================================================
# APINFO
# ============================================================

APINFO_URL = "https://www.apinfo.com/"


# ============================================================
# PALAVRAS-CHAVE
# ============================================================

KEYWORDS = {

    "Suporte": [
        "suporte técnico",
        "suporte de ti",
        "suporte ti",
        "analista de suporte",
        "analista de suporte técnico",
        "suporte n1",
        "suporte n2",
        "suporte nível 1",
        "suporte nível 2",
        "help desk",
        "helpdesk",
        "service desk",
        "técnico de suporte",
        "técnico de informática",
        "assistente de suporte",
        "assistente de ti",
    ],

    "Infraestrutura": [
        "infraestrutura",
        "infraestrutura de ti",
        "infraestrutura de tecnologia",
        "analista de infraestrutura",
        "assistente de infraestrutura",
        "técnico de infraestrutura",
        "infraestrutura de redes",
    ],

    "Sistemas": [
        "windows",
        "windows server",
        "linux",
        "ubuntu",
        "ubuntu server",
        "sistema operacional",
        "sistemas operacionais",
    ],

    "Microsoft / AD": [
        "active directory",
        "ad microsoft",
        "microsoft 365",
        "office 365",
        "m365",
        "azure ad",
        "entra id",
    ],

    "Redes": [
        "redes",
        "rede de computadores",
        "redes de computadores",
        "infraestrutura de redes",
        "tcp/ip",
        "tcp ip",
        "dns",
        "dhcp",
        "firewall",
        "roteador",
        "switch",
        "lan",
        "wan",
        "vpn",
    ],

    "Hardware": [
        "hardware",
        "manutenção de computadores",
        "manutenção de hardware",
        "periféricos",
        "computadores",
        "notebooks",
        "desktop",
        "montagem de computadores",
        "troubleshooting",
    ],

    "Servidores": [
        "servidor",
        "servidores",
        "administração de servidores",
        "administrador de servidores",
        "administrador de sistemas",
        "administração de sistemas",
        "sysadmin",
        "system administrator",
    ],

    "Backup": [
        "backup",
        "rotina de backup",
        "backup de servidores",
        "restauração de backup",
    ],

    "Automação / DevOps": [
        "automação",
        "automação de infraestrutura",
        "ansible",
        "devops",
        "docker",
        "virtualização",
        "virtualbox",
        "vmware",
        "hyper-v",
    ],

    "Desenvolvimento": [
        "python",
        "script python",
        "automação python",
        "sql",
        "javascript",
    ],
}


# ============================================================
# TERMOS DE EXCLUSÃO
# ============================================================

EXCLUDE_KEYWORDS = [
    "gerente de ti",
    "gerente de tecnologia",
    "coordenador de ti",
    "coordenador de infraestrutura",
    "diretor de ti",
    "diretor de tecnologia",
    "tech lead",
    "staff engineer",
    "principal engineer",
    "arquiteto de software",
]


# ============================================================
# PESOS
# ============================================================

CATEGORY_WEIGHTS = {
    "Suporte": 5,
    "Infraestrutura": 5,
    "Redes": 4,
    "Sistemas": 4,
    "Microsoft / AD": 4,
    "Servidores": 4,
    "Hardware": 3,
    "Backup": 3,
    "Automação / DevOps": 3,
    "Desenvolvimento": 1,
}


# ============================================================
# SCORE MÍNIMO
# ============================================================

MINIMUM_SCORE = 5


# ============================================================
# ARQUIVO DE DEDUPLICAÇÃO
# ============================================================

SEEN_JOBS_FILE = (
    BASE_DIR /
    "data" /
    "seen_jobs.json"
)
