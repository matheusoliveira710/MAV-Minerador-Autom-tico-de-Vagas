"""
Módulo de Notificação via Discord Webhook para o MAV.
Responsável exclusivamente por formatar e disparar embeds formatados de vagas relevantes,
tratando erros de rede, timeouts e protegendo credenciais.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Optional
from models import Job
from matcher import MatchResult


# Classificações que elegem a vaga para notificação no Discord
ELIGIBLE_CLASSIFICATIONS = {"RELEVANTE", "MUITO RELEVANTE", "EXCELENTE"}


def is_job_eligible_for_notification(match_result: MatchResult) -> bool:
    """Verifica se a classificação da vaga atinge o patamar mínimo para notificação."""
    if not match_result or not getattr(match_result, 'classification', None):
        return False
    return match_result.classification.upper() in ELIGIBLE_CLASSIFICATIONS


def format_job_embed(job: Job, match_result: MatchResult) -> dict:
    """Formata os dados do Job e do MatchResult em um Discord Embed estruturado."""
    roles = getattr(match_result, 'matched_roles', []) or []
    core_skills = getattr(match_result, 'matched_core_skills', []) or []

    fields = [
        {"name": "🏢 Empresa", "value": job.company or "Não informada", "inline": True},
        {"name": "📍 Local", "value": job.location or "Não informado", "inline": True},
        {"name": "🎯 Classificação", "value": getattr(match_result, 'classification', 'DESCONHECIDA'), "inline": True},
        {"name": "⭐ Score", "value": f"{getattr(match_result, 'score', 0.0):.1f}", "inline": True},
        {"name": "💼 Cargos Reconhecidos", "value": ", ".join(roles) or "Nenhum", "inline": False},
        {"name": "🛠️ Core Skills", "value": ", ".join(core_skills) or "Nenhuma detectada", "inline": False}
    ]

    if job.link:
        fields.append({"name": "🔗 Link da Vaga", "value": f"[Acessar Vaga]({job.link})", "inline": False})

    embed = {
        "title": f"🚨 NOVA VAGA — MAV: {job.title}",
        "color": 3447003,
        "fields": fields,
        "footer": {"text": f"Origem: {job.source} | ID: {job.unique_id()[:8]}"}
    }
    return {"embeds": [embed]}


def send_job_to_discord(job: Job, match_result: MatchResult, webhook_url: Optional[str] = None, timeout: int = 5) -> bool:
    """
    Envia a vaga relevante para o Discord Webhook utilizando URL configurada por ambiente.
    Trata falhas de rede, timeouts e ausência de webhook de forma controlada.
    """
    if webhook_url is None:
        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        return False

    if not is_job_eligible_for_notification(match_result):
        return False

    payload = format_job_embed(job, match_result)
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "MAV-Bot/1.0"}
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return 200 <= response.status < 300
    except (urllib.error.HTTPError, urllib.error.URLError, Exception):
        return False
