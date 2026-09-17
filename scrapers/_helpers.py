"""
MAV — HELPERS DO PIPELINE DE SCRAPING
Gerencia a normalização, deduplicação, matching e o disparo de alertas via Insight MAV.
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "data" / "config.json"


def get_telegram_notifier():
    """Carrega as credenciais e instancia o notificador Insight MAV de forma segura."""
    if not CONFIG_FILE.exists():
        return None
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            config = json.load(f)
            token = config.get("telegram_token")
            chat_id = config.get("telegram_chat_id")
            if token and chat_id and token != "SEU_TOKEN_DO_BOT_AQUI":
                from notifier import TelegramNotifier
                return TelegramNotifier(token=token, chat_id=chat_id)
    except Exception:
        pass
    return None

def process_scraped_pipeline(raw_jobs, seen_ids, matcher):
    """
    Processa a lista de vagas brutas ou objetos Job: normaliza, evita duplicatas,
    executa o matcher e dispara o alerta via Insight MAV se elegível.
    """
    from models import Job
    
    results = []
    notifier = get_telegram_notifier()

    for item in raw_jobs:
        # Suporta tanto dicionários brutos quanto instâncias diretas de Job
        if isinstance(item, Job):
            job_norm = item.normalize()
        else:
            job = Job(
                title=item.get("title", ""),
                company=item.get("company", "Empresa não informada"),
                location=item.get("location", "Campinas, SP"),
                link=item.get("link", ""),
                source=item.get("source", "Portal"),
                description_snippet=item.get("description_snippet", "")
            )
            job_norm = job.normalize()

        unique_id = f"{job_norm.title}_{job_norm.company}".lower()

        if unique_id in seen_ids:
            continue
        seen_ids.add(unique_id)

        # Executa a análise do Matcher usando .match() corretamente
        match_result = matcher.match(job_norm)

        # Se for relevante, armazena e notifica via Insight MAV
        if match_result.score >= 70.0:
            results.append((job_norm, match_result))
            
            if notifier:
                job_data = {
                    "title": job_norm.title,
                    "company": job_norm.company,
                    "location": job_norm.location,
                    "source": job_norm.source,
                    "link": job_norm.link,
                    "description_snippet": job_norm.description_snippet
                }
                notifier.send_job_alert(job_data, match_result, is_golden_window=True)

    return results