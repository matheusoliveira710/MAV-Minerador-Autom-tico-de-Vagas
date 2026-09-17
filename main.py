import argparse
import asyncio
import csv
from datetime import datetime
import inspect
import json
from pathlib import Path
import sys
import time

from patchright.async_api import async_playwright

from config import (
    SEEN_JOBS_FILE,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)
from matcher import JobMatcher
from notifier import TelegramNotifier
from scrapers import ALL_SCRAPERS

# Configuração do Event Loop para Windows 11
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


# ============================================================
# DIRETÓRIOS E CONSTANTES DO CSV
# ============================================================

DATA_DIR = Path(__file__).resolve().parent / "data"
VAGAS_CSV_FILE = DATA_DIR / "vagas_mineradas.csv"
BROWSER_PROFILE_DIR = DATA_DIR / "browser_profile"


# ============================================================
# MODELO DE VAGA
# ============================================================

class JobModel:
    def __init__(self, data: dict):
        self.site = str(data.get("site") or "ApInfo")
        self.source = self.site

        raw_title = str(data.get("title") or "").strip()
        raw_company = str(data.get("company") or "").strip()
        raw_location = str(data.get("location") or "").strip()
        
        if " - " in raw_title and any(char.isdigit() for char in raw_title):
            self.location = raw_title
            self.title = raw_company
            self.company = str(data.get("empresa") or data.get("company") or f"Confidencial / {self.site}")
        else:
            self.title = raw_company if raw_company and not any(char.isdigit() for char in raw_company) else raw_title
            self.company = raw_title if raw_title and raw_title != self.title else f"Confidencial / {self.site}"
            self.location = raw_location

        self.search_term = str(data.get("search_term") or "")
        self.code = str(data.get("code") or "00000")
        self.link = str(data.get("link") or "")
        self.raw_text = str(data.get("raw_text") or "")

    def unique_id(self) -> str:
        return f"{self.site}_{self.code}_{self.title}_{self.company}"


# ============================================================
# ARGUMENTOS
# ============================================================

def parse_args():
    sites_keys = list(ALL_SCRAPERS.keys())
    available_choices = sites_keys + [k.lower() for k in sites_keys] + ["all", "ALL"]
    
    parser = argparse.ArgumentParser(
        description="MAV — Minerador Automático de Vagas | Scraper -> Matcher -> Telegram"
    )

    parser.add_argument(
        "--site",
        default="all",
        choices=available_choices,
        help="Plataforma a consultar ('all' para executar todos os scrapers).",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Executa todo o pipeline sem enviar vagas para o Telegram.",
    )

    parser.add_argument(
        "--headed",
        action="store_true",
        help="Abre o navegador visivelmente.",
    )

    return parser.parse_args()


# ============================================================
# CARREGAR DEDUPLICAÇÃO
# ============================================================

def load_seen_jobs() -> set[str]:
    if not SEEN_JOBS_FILE.exists():
        return set()

    try:
        with open(SEEN_JOBS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            return set()

        return {str(item) for item in data}

    except (OSError, json.JSONDecodeError) as error:
        print(f"[DEDUP] Erro ao ler arquivo: {error}")
        return set()


# ============================================================
# SALVAR DEDUPLICAÇÃO
# ============================================================

def save_seen_jobs(seen: set[str]):
    SEEN_JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(SEEN_JOBS_FILE, "w", encoding="utf-8") as file:
        json.dump(sorted(seen), file, ensure_ascii=False, indent=2)


# ============================================================
# SALVAR CSV
# ============================================================

def salvar_vagas_para_csv(new_jobs):
    if not new_jobs:
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_exists = VAGAS_CSV_FILE.exists()
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            with open(VAGAS_CSV_FILE, mode="a", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["DataHora", "Site", "Termo", "Cargo", "Empresa", "Localizacao", "Codigo", "Link"])
                
                for job, _ in new_jobs:
                    writer.writerow([
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        job.source,
                        job.search_term,
                        job.title,
                        job.company,
                        job.location,
                        job.code,
                        job.link
                    ])
            print(f"[CSV] Base CSV atualizada com sucesso: {VAGAS_CSV_FILE}")
            break
        except PermissionError:
            if attempt < max_retries - 1:
                print(f"[CSV] Arquivo ocupado pelo Scheduler. Tentativa {attempt + 1}/{max_retries} em 0.5s...")
                time.sleep(0.5)
            else:
                print("[CSV] ❌ Falha: Não foi possível escrever no CSV (bloqueio mantido).")
        except Exception as e:
            print(f"[CSV] Erro ao salvar arquivo CSV: {e}")
            break


# ============================================================
# MATCHER
# ============================================================

def match_jobs(jobs):
    matcher = JobMatcher()
    matched_jobs = []

    print()
    print("=" * 65)
    print("MATCHER")
    print("=" * 65)

    for index, job in enumerate(jobs, start=1):
        try:
            result = matcher.match(job)
            matched_jobs.append((job, result))

            print(f"[MATCH] {index}/{len(jobs)} | {job.title}")
            print(f"        Score: {result.score:.1f}")
            print(f"        Classificação: {result.classification}")
            print(f"        Cargos: {', '.join(result.matched_roles) or 'Nenhum'}")
            print(f"        Core Skills: {', '.join(result.matched_core_skills) or 'Nenhuma'}")

        except Exception as error:
            print(f"[MATCH] ✗ Falha ao analisar {job.title}. Erro: {error}")

    return matched_jobs


# ============================================================
# DEDUPLICAÇÃO
# ============================================================

def deduplicate_jobs(matched_jobs, seen: set[str]):
    new_jobs = []
    duplicates = 0

    for job, match_result in matched_jobs:
        job_id = job.unique_id()

        if job_id in seen:
            duplicates += 1
            print(f"[DEDUP] ↻ Já processada: {job.title}")
            continue

        new_jobs.append((job, match_result))
        seen.add(job_id)

    print()
    print(f"[DEDUP] Já processadas: {duplicates}")
    print(f"[DEDUP] Novas vagas: {len(new_jobs)}")

    return new_jobs


# ============================================================
# TELEGRAM NOTIFIER
# ============================================================

def notify_telegram(matched_jobs, dry_run: bool):
    print()
    print("=" * 65)
    print("TELEGRAM")
    print("=" * 65)

    sent = 0
    blocked = 0
    failed = 0

    notifier = TelegramNotifier(
        token=TELEGRAM_BOT_TOKEN,
        chat_id=TELEGRAM_CHAT_ID
    )

    for job, match_result in matched_jobs:
        classification = str(getattr(match_result, 'classification', '')).upper()
        eligible = match_result.score > 0.0 and classification != "DESCARTAR"

        print()
        print(f"[TELEGRAM] {job.title}")
        print(f"          Score: {match_result.score:.1f}")
        print(f"          Classificação: {match_result.classification}")

        if not eligible:
            blocked += 1
            print("[TELEGRAM] ✗ Não elegível para notificação (Score zero ou descartada).")
            continue

        if dry_run:
            print("[TELEGRAM] ✓ Elegível — DRY-RUN. API do Telegram não será acionada.")
            continue

        job_data = {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "source": job.source,
            "link": job.link,
        }

        success = notifier.send_job_alert(
            job_data=job_data,
            match_result=match_result,
            is_golden_window=True
        )

        if success:
            sent += 1
            print("[TELEGRAM] ✓ Alerta enviado com sucesso para o Telegram.")
        else:
            failed += 1
            print("[TELEGRAM] ✗ Falha ao enviar alerta para o Telegram.")

    print()
    print(f"[TELEGRAM] Enviadas: {sent}")
    print(f"[TELEGRAM] Bloqueadas: {blocked}")
    print(f"[TELEGRAM] Falhas: {failed}")

    return sent, blocked, failed


# ============================================================
# MAIN ASSÍNCRONO
# ============================================================

async def main():
    args = parse_args()

    if args.site.lower() == "all":
        sites_to_run = list(ALL_SCRAPERS.keys())
    else:
        matching_site = next((k for k in ALL_SCRAPERS.keys() if k.lower() == args.site.lower()), args.site)
        sites_to_run = [matching_site]

    print()
    print("=" * 65)
    print("MAV — MINERADOR AUTOMÁTICO DE VAGAS")
    print("=" * 65)
    print(f"Sites selecionados: {', '.join(sites_to_run)}")
    print(f"Dry-run: {args.dry_run}")
    print(f"Headed: {args.headed}")
    print("=" * 65)

    seen = load_seen_jobs()
    BROWSER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    
    totais = {
        "coletadas": 0,
        "analisadas": 0,
        "novas": 0,
        "enviadas": 0,
        "bloqueadas": 0,
        "falhas": 0
    }

    async with async_playwright() as p:
        # Inicializa o contexto persistente usando o perfil salvo e o canal nativo do Chrome
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_PROFILE_DIR),
            headless=not args.headed,
            channel="chrome",
            viewport={"width": 1366, "height": 768},
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-infobars",
                "--ignore-certificate-errors",
            ]
        )

        for current_site in sites_to_run:
            print(f"\n🚀 [MAIN] Iniciando raspagem no portal: {current_site}")
            
            scraper = ALL_SCRAPERS.get(current_site)
            if not scraper:
                print(f"[MAIN] ❌ Scraper não encontrado para: {current_site}")
                continue

            jobs = []
            page = await context.new_page()

            try:
                if inspect.iscoroutinefunction(scraper):
                    raw_jobs = await scraper(page)
                else:
                    result = scraper(page)
                    raw_jobs = await result if inspect.isawaitable(result) else result

                jobs = [JobModel(j) if isinstance(j, dict) else j for j in raw_jobs]

            except Exception as error:
                print(f"[MAIN] ❌ Falha inesperada no scraper {current_site}: {error}")
                jobs = []
            finally:
                await page.close()

            print(f"[MAIN] Vagas coletadas [{current_site}]: {len(jobs)}")
            totais["coletadas"] += len(jobs)

            if not jobs:
                continue

            # Processamento do pipeline
            matched_jobs = match_jobs(jobs)
            totais["analisadas"] += len(matched_jobs)

            if not matched_jobs:
                continue

            new_jobs = deduplicate_jobs(matched_jobs, seen)
            totais["novas"] += len(new_jobs)

            if not new_jobs:
                continue

            sent, blocked, failed = notify_telegram(new_jobs, dry_run=args.dry_run)
            totais["enviadas"] += sent
            totais["bloqueadas"] += blocked
            totais["falhas"] += failed

            salvar_vagas_para_csv(new_jobs)

        await context.close()

    # Atualização final do banco de deduplicação se não for dry-run
    if not args.dry_run and totais["novas"] > 0:
        save_seen_jobs(seen)
        print(f"\n[DEDUP] Banco atualizado com sucesso: {SEEN_JOBS_FILE}")

    # Resumo Geral
    print()
    print("=" * 65)
    print("RESUMO CONSOLIDADO DA EXECUÇÃO")
    print("=" * 65)
    print(f"Vagas coletadas: {totais['coletadas']}")
    print(f"Vagas analisadas: {totais['analisadas']}")
    print(f"Vagas novas: {totais['novas']}")
    print(f"Enviadas ao Telegram: {totais['enviadas']}")
    print(f"Bloqueadas pelo notifier: {totais['bloqueadas']}")
    print(f"Falhas de envio: {totais['falhas']}")
    print()
    print("[MAIN] Execução concluída com sucesso.")

    return 0


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))