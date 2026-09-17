import requests
from bs4 import BeautifulSoup

def programathor_scraper(page=None):
    """Scraper para o Programathor via BeautifulSoup."""
    url = "https://programathor.com.br/jobs?q=Suporte"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    raw_jobs = []

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        cards = soup.select(".cell-list")
        for card in cards:
            link_elem = card.select_one("a[href^='/jobs/']")
            if not link_elem:
                continue

            link = f"https://programathor.com.br{link_elem['href']}"
            title_elem = card.select_one("h3")
            info_spans = card.select(".cell-list-content span")

            company = info_spans[0].get_text(strip=True) if len(info_spans) > 0 else "Confidencial"
            location = info_spans[1].get_text(strip=True) if len(info_spans) > 1 else "Remoto / BR"

            job_id = link_elem['href'].split('/')[2] if len(link_elem['href'].split('/')) > 2 else "00000"

            raw_jobs.append({
                "title": title_elem.get_text(strip=True) if title_elem else "Não informado",
                "company": company,
                "location": location,
                "site": "Programathor",
                "link": link,
                "code": f"prog_{job_id}",
                "raw_text": f"{title_elem.get_text(strip=True) if title_elem else ''} - {company}"
            })

        print(f"[PROGRAMATHOR] {len(raw_jobs)} vagas obtidas.")
        return raw_jobs

    except Exception as e:
        print(f"[PROGRAMATHOR] Erro ao raspar: {e}")
        return []