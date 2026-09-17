"""
MAV — TESTE REAL DO DISCORD WEBHOOK

ATENÇÃO:
- Este teste envia UMA mensagem real para o Discord.
- Nunca coloque o Webhook diretamente neste arquivo.
- O Webhook deve estar no arquivo .env.
- O Webhook NÃO deve ser exibido no terminal.

Execução:
    python -m tests.test_discord_real
"""

import os

# Importar config primeiro para carregar o .env
import config

from models import Job
from matcher import JobMatcher
from discord_notifier import (
    is_job_eligible_for_notification,
    send_job_to_discord,
)


def main():
    print("=" * 70)
    print("MAV — TESTE REAL DISCORD WEBHOOK")
    print("=" * 70)

    # ================================================================
    # 1. VERIFICAR WEBHOOK
    # ================================================================

    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        print()
        print("❌ ERRO: DISCORD_WEBHOOK_URL não configurado.")
        print()
        print("Verifique o arquivo .env na raiz do projeto.")
        print("Formato esperado:")
        print()
        print("DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...")
        print()
        return 1

    print()
    print("Webhook configurado: SIM")
    print("Webhook exibido: NÃO (proteção de segredo)")
    print()

    # ================================================================
    # 2. CRIAR VAGA DE TESTE
    # ================================================================

    job = Job(
        title="Analista de Suporte Júnior",
        company="MAV — Empresa de Teste",
        location="Campinas - SP",
        description=(
            "Atendimento e suporte técnico aos usuários. "
            "Manutenção de notebooks e computadores. "
            "Suporte Windows 11, Active Directory, "
            "troubleshooting, gestão de chamados e acesso remoto."
        ),
        requirements=(
            "Suporte técnico, Windows 11, Active Directory, "
            "Hardware, Troubleshooting, Gestão de chamados."
        ),
        source="TESTE_DISCORD",
        url="https://example.com/vaga-teste-mav",
    )

    print("Vaga de teste:")
    print(f"  Cargo: {job.title}")
    print(f"  Empresa: {job.company}")
    print(f"  Local: {job.location}")
    print()

    # ================================================================
    # 3. EXECUTAR MATCHER
    # ================================================================

    print("Executando JobMatcher...")

    matcher = JobMatcher()
    match_result = matcher.match(job)

    print()
    print(f"Score: {match_result.score:.1f}")
    print(f"Classificação: {match_result.classification}")

    # ================================================================
    # 4. VERIFICAR ELEGIBILIDADE
    # ================================================================

    eligible = is_job_eligible_for_notification(match_result)

    print(f"Elegível para Discord: {'SIM' if eligible else 'NÃO'}")
    print()

    if not eligible:
        print("❌ TESTE INTERROMPIDO")
        print("A vaga de teste não atingiu classificação elegível.")
        return 1

    # ================================================================
    # 5. ENVIO REAL
    # ================================================================

    print("Enviando vaga para o Discord...")
    print()

    success = send_job_to_discord(
        job=job,
        match_result=match_result,
        webhook_url=webhook_url,
        timeout=5,
    )

    # ================================================================
    # 6. RESULTADO
    # ================================================================

    print()

    if success:
        print("HTTP/Webhook: SUCESSO")
        print()
        print("✅ Mensagem enviada com sucesso para o Discord!")
        print()
        print("Verifique o canal configurado para o Webhook.")
        print()
        print("=" * 70)
        print("TESTE REAL DISCORD: APROVADO")
        print("=" * 70)
        return 0

    print("❌ Falha ao enviar mensagem para o Discord.")
    print()
    print("Possíveis causas:")
    print("- Webhook inválido")
    print("- Webhook removido")
    print("- Problema de conexão")
    print("- Timeout")
    print("- Discord indisponível")
    print()
    print("=" * 70)
    print("TESTE REAL DISCORD: FALHOU")
    print("=" * 70)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

