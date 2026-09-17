"""
MAV — ANSIBLE MANAGER
Módulo de Integração e Execução de Playbooks Ansible para o Home Lab.
Compatível com Python 3.12 e Windows 11.
"""
from __future__ import annotations
import logging
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ANSIBLE_DIR = BASE_DIR / "ansible"  # Diretório onde ficarão seus playbooks e hosts
ANSIBLE_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("MAV-ANSIBLE")

def verificar_instalacao_ansible() -> bool:
    """Verifica se o Ansible está acessível no ambiente."""
    try:
        result = subprocess.run(["ansible", "--version"], capture_output=True, text=True, check=False)
        return result.returncode == 0
    except Exception:
        return False


def executar_playbook(nome_playbook: str, inventario: str = "hosts.ini") -> dict:
    """
    Executa um playbook Ansible localizado na pasta ansible/ e retorna o resultado estruturado.
    """
    playbook_path = ANSIBLE_DIR / nome_playbook
    inventario_path = ANSIBLE_DIR / inventario

    if not playbook_path.exists():
        msg_erro = f"Playbook '{nome_playbook}' não encontrado em {ANSIBLE_DIR}."
        logger.error(msg_erro)
        return {"sucesso": False, "saida": msg_erro, "codigo": -1}

    comando = ["ansible-playbook", str(playbook_path)]
    if inventario_path.exists():
        comando.extend(["-i", str(inventario_path)])

    logger.info("Executando Ansible: %s", " ".join(comando))
    
    try:
        result = subprocess.run(
            comando,
            cwd=ANSIBLE_DIR,
            capture_output=True,
            text=True,
            timeout=300  # Timeout de segurança de 5 minutos
        )
        
        sucesso = result.returncode == 0
        saida_completa = result.stdout + "\n" + result.stderr
        
        if sucesso:
            logger.info("Playbook '%s' executado com sucesso.", nome_playbook)
        else:
            logger.error("Playbook '%s' falhou com código %d.", nome_playbook, result.returncode)

        return {
            "sucesso": sucesso,
            "saida": saida_completa.strip(),
            "codigo": result.returncode
        }

    except subprocess.TimeoutExpired:
        logger.error("A execução do playbook '%s' excedeu o tempo limite (timeout).", nome_playbook)
        return {"sucesso": False, "saida": "Erro: Timeout excedido (mais de 5 minutos).", "codigo": -2}
    except Exception as e:
        logger.exception("Erro crítico ao rodar Ansible.")
        return {"sucesso": False, "saida": str(e), "codigo": -3}


def gerar_relatorio_ansible_texto() -> str:
    """Gera um resumo formatado para o Telegram sobre o estado do Ansible no projeto."""
    instalado = verificar_instalacao_ansible()
    status_emoji = "🟢" if instalado else "🔴"
    status_texto = "Instalado e Operacional" if instalado else "Não detectado no PATH"

    playbooks_disponiveis = [p.name for p in ANSIBLE_DIR.glob("*.yml")] + [p.name for p in ANSIBLE_DIR.glob("*.yaml")]

    relatorio = (
        f"⚙️ *MODULO ANSIBLE MANAGER — HOME LAB*\n\n"
        f"• *Status Binário:* {status_emoji} `{status_texto}`\n"
        f"• *Diretório Alvo:* `{ANSIBLE_DIR}`\n"
        f"• *Playbooks Disponíveis:* `{len(playbooks_disponiveis)}`\n"
    )

    if playbooks_disponiveis:
        relatorio += "• *Listagem:* " + ", ".join([f"`{p}`" for p in playbooks_disponiveis]) + "\n"
    else:
        relatorio += "• *Aviso:* Nenhum playbook `.yml` encontrado na pasta `ansible/`.\n"

    return relatorio