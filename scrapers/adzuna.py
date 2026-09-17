import requests
from config import ADZUNA_APP_ID, ADZUNA_APP_KEY

def adzuna_scraper(page=None):
    """Scraper do Adzuna via API REST."""
    url = "https://api.adzuna.com/v1/api/jobs/br/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 20,
        "what": "Suporte TI Helpdesk",
        "content-type": "application/json"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        raw_jobs = []
        for result in data.get("results", []):
            raw_jobs.append({
                "title": result.get("title", ""),
                "company": result.get("company", {}).get("display_name", "Confidencial"),
                "location": result.get("location", {}).get("display_name", "Brasil"),
                "site": "Adzuna",
                "link": result.get("redirect_url", ""),
                "code": str(result.get("id", "00000")),
                "raw_text": result.get("description", "")
            })
            
        print(f"[ADZUNA] {len(raw_jobs)} vagas obtidas via API.")
        return raw_jobs

    except Exception as e:
        print(f"[ADZUNA] Erro ao consultar API: {e}")
        return []

if __name__ == "__main__":
    vagas = adzuna_scraper()
    print(f"\n[TESTE] Total de vagas retornadas: {len(vagas)}")
    if vagas:
        print("[TESTE] Exemplo da primeira vaga encontrada:")
        print(vagas[0])