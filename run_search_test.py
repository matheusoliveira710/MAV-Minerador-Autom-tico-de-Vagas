"""
MAV — SCRIPT DE TESTE DE BUSCA REAL UNIFICADO (DRY-RUN)
Executa os scrapers reais (ApInfo e Infojobs), normaliza, deduplica, 
aplica o Matcher e exibe os resultados detalhados no console sem disparar o Discord.
"""

from matcher import JobMatcher
from scrapers.apinfo import scrape_apinfo
from scrapers.infojobs import InfojobsScraper
from browser_utils import BrowserManager
from models import Job


def run_live_search_test():
    print("=" * 70)
    print("🛡️ PROTOCOLO SENTINELA — INICIANDO BUSCA REAL UNIFICADA")
    print("=" * 70)

    matcher = JobMatcher()
    seen_ids = set()
    all_raw_jobs = []

    # 1. Varredura no ApInfo utilizando o BrowserManager oficial
    print("\n[SENTINELA] Conectando ao ApInfo...")
    manager = BrowserManager(headless=True)
    try:
        page = manager.start()
        apinfo_jobs = scrape_apinfo(page)
        print(f"[APINFO] Vagas brutas coletadas: {len(apinfo_jobs)}")
        all_raw_jobs.extend(apinfo_jobs)
    except Exception as e:
        print(f"[ERRO] Falha ao coletar do ApInfo: {e}")
    finally:
        manager.close()

    # 2. Varredura no Infojobs
    print("\n[SENTINELA] Conectando ao Infojobs...")
    try:
        infojobs_scraper = InfojobsScraper(headless=True)
        ij_raw = infojobs_scraper.scrape(keyword="suporte ti", location="Campinas", max_jobs=10)
        
        for item in ij_raw:
            j = Job(
                title=item["title"],
                company=item["company"],
                location=item["location"],
                link=item["link"],
                source=item["source"],
                description_snippet=item["description_snippet"]
            )
            all_raw_jobs.append(j)
            
        print(f"[INFOJOBS] Vagas brutas coletadas: {len(ij_raw)}")
    except Exception as e:
        print(f"[ERRO] Falha ao coletar do Infojobs: {e}")

    print(f"\n[SENTINELA] Total de vagas brutas acumuladas: {len(all_raw_jobs)}")
    print("-" * 70)

    # 3. Processamento pelo Pipeline do Matcher
    print("\n[SENTINELA] Aplicando Normalização, Deduplicação e Matcher...")
    
    valid_matches = []
    for job in all_raw_jobs:
        norm_job = job.normalize()
        
        jid = norm_job.unique_id()
        if jid in seen_ids:
            continue
        seen_ids.add(jid)

        match_result = matcher.match(norm_job)

        if match_result.classification in {"RELEVANTE", "MUITO RELEVANTE", "EXCELENTE"}:
            valid_matches.append((norm_job, match_result))

    print("\n" + "=" * 70)
    print(f"🎯 RESULTADOS DA BUSCA — VAGAS ELEGÍVEIS ENCONTRADAS: {len(valid_matches)}")
    print("=" * 70)

    for idx, (job, match) in enumerate(valid_matches, 1):
        print(f"\n[{idx}] {job.title}")
        print(f"    🏢 Empresa: {job.company}")
        print(f"    📍 Local: {job.location}")
        print(f"    ⭐ Score: {match.score:.1f} | Classificação: {match.classification}")
        print(f"    🌐 Origem: {job.source}")
        print(f"    🔗 Link: {job.link}")
        print(f"    🛠️ Core Skills: {', '.join(match.matched_core_skills) or 'Nenhuma'}")
        print("-" * 70)

    print("\n✅ Teste de busca real unificado concluído com sucesso, senhor!")


if __name__ == "__main__":
    run_live_search_test()