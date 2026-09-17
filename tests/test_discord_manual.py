from dotenv import load_dotenv

from models import Job
from matcher import JobMatcher
from discord_notifier import send_job_to_discord


load_dotenv()

print("=" * 60)
print("MAV — TESTE REAL DO DISCORD WEBHOOK")
print("=" * 60)


# ============================================================
# VAGA DE TESTE
# ============================================================

job = Job(
    title="Gerente Comercial",
    company="Empresa Teste",
    location="Campinas - SP",
    link="https://exemplo.com/vaga",
    source="Teste Manual",
    description_snippet=(
        "Responsável por vendas, metas comerciais, "
        "gestão de equipe e estratégias comerciais."
    ),
)


# ============================================================
# MATCHER REAL
# ============================================================

matcher = JobMatcher()

match_result = matcher.match(job)


# ============================================================
# EXIBIÇÃO
# ============================================================

print()
print("Vaga:")
print(f"  Cargo: {job.title}")
print(f"  Empresa: {job.company}")
print(f"  Local: {job.location}")

print()
print("Match REAL:")
print(f"  Score: {match_result.score}")
print(f"  Classificação: {match_result.classification}")

print()
print("Cargos reconhecidos:")
print(f"  {match_result.matched_roles}")

print()
print("Core Skills:")
print(f"  {match_result.matched_core_skills}")

print()
print("Penalizações:")
print(f"  {match_result.penalties}")

print()
print("Razões:")
for reason in match_result.reasons:
    print(f"  - {reason}")


# ============================================================
# ENVIO
# ============================================================

print()
print("Enviando para o Discord...")

success = send_job_to_discord(
    job,
    match_result,
)


# ============================================================
# RESULTADO
# ============================================================

print()

if success:
    print("⚠️ WEBHOOK ENVIADO.")
    print("⚠️ ATENÇÃO: essa vaga foi considerada elegível.")
else:
    print("✅ WEBHOOK NÃO ENVIADO.")
    print("✅ Vaga corretamente bloqueada pelo notifier.")

print("=" * 60)
