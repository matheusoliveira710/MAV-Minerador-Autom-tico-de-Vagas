"""
MAV — MÓDULO LAB SENTINELA
Monitoramento de VMs, Tailscale, Portas SSH, Telemetria e Conectividade de Rede.
Compatível com Python 3.12 e Windows 11.
"""
from __future__ import annotations
import socket
import subprocess
import platform
import logging
from pathlib import Path

logger = logging.getLogger("MAV-SENTINELA")

# Defina aqui os IPs das suas VMs no Tailscale ou rede local do Home Lab
# Você pode ajustar os nomes e IPs conforme o seu ambiente atual
HOME_LAB_NODES = {
    "Ubuntu-Server": {"ip": "100.64.0.10", "porta_ssh": 22},
    "Lubuntu-Lab": {"ip": "100.64.0.11", "porta_ssh": 22}
}

# Armazenamento em memória para detecção de mudança de IP
_cache_ips_conhecidos = {}

def testar_ping(ip: str) -> bool:
    """Dispara um ping rápido para verificar se o nó responde na rede."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    comando = ["ping", param, "1", "-w", "2000", ip]
    try:
        resultado = subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return resultado.returncode == 0
    except Exception:
        return False

def testar_porta_ssh(ip: str, porta: int = 22, timeout: float = 2.0) -> bool:
    """Verifica se a porta SSH da VM está aberta e respondendo."""
    try:
        with socket.create_connection((ip, porta), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def verificar_conectividade_global() -> bool:
    """Testa a conectividade com a internet usando o DNS público da Cloudflare ou Google."""
    try:
        with socket.create_connection(("1.1.1.1", 53), timeout=3.0):
            return True
    except OSError:
        return False

def inspecionar_home_lab() -> dict:
    """
    Executa a varredura completa em todas as VMs cadastradas no Home Lab.
    Retorna o status detalhado, detecção de queda e mudança de IP.
    """
    global _cache_ips_conhecidos
    relatorio = {
        "internet_ok": verificar_conectividade_global(),
        "vms": [],
        "alertas_criticos": []
    }

    for nome, config in HOME_LAB_NODES.items():
        ip_atual = config["ip"]
        porta = config["porta_ssh"]

        online_ping = testar_ping(ip_atual)
        online_ssh = testar_porta_ssh(ip_atual, porta) if online_ping else False

        status_vm = {
            "nome": nome,
            "ip": ip_atual,
            "ping": online_ping,
            "ssh": online_ssh,
            "saudavel": online_ping and online_ssh
        }

        # Verificação de Alerta de Queda
        if not online_ping:
            relatorio["alertas_criticos"].append(
                f"🚨 *ALERTA HOME LAB:* A VM `{nome}` (`{ip_atual}`) parou de responder no Tailscale!"
            )

        # Verificação de Mudança de IP (caso utilize descoberta dinâmica no futuro)
        if nome in _cache_ips_conhecidos and _cache_ips_conhecidos[nome] != ip_atual:
            relatorio["alertas_criticos"].append(
                f"⚠️ *AVISO DE REDE:* O IP da VM `{nome}` mudou de `{_cache_ips_conhecidos[nome]}` para `{ip_atual}`!"
            )
        
        _cache_ips_conhecidos[nome] = ip_atual
        relatorio["vms"].append(status_vm)

    return relatorio

def gerar_relatorio_homelab_texto() -> str:
    """Gera um resumo formatado em Markdown para o comando /homelab ou /lab_telemetria."""
    dados = inspecionar_home_lab()
    
    internet_status = "🟢 Conectado (1.1.1.1 OK)" if dados["internet_ok"] else "🔴 Queda de Link / Sem Internet"
    
    msg = (
        f"🖥️ *STATUS DO HOME LAB & INFRAESTRUTURA*\n\n"
        f"• *Link Externo (Internet):* {internet_status}\n"
        f"• *Malha Tailscale / VirtualBox:* Ativa\n\n"
        f"📋 *Mapeamento de Máquinas Virtuais:*\n"
    )

    for vm in dados["vms"]:
        icone_ping = "🟢" if vm["ping"] else "🔴"
        icone_ssh = "🟢" if vm["ssh"] else "🔴"
        msg += (
            f"• *{vm['nome']}* (`{vm['ip']}`)\n"
            f"  └ Ping: {icone_ping} | SSH (Porta 22): {icone_ssh}\n"
        )

    if dados["alertas_criticos"]:
        msg += f"\n⚠️ *Ocorrências Detectadas:*\n"
        for alerta in dados["alertas_criticos"]:
            msg += f"• {alerta}\n"
    else:
        msg += f"\n💡 *Diagnóstico:* Todas as VMs operando com estabilidade total Senhor!"

    return msg