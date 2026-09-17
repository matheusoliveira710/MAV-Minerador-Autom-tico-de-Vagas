"""
MAV — SCRAPER DA CATHO
Responsável por varrer as páginas de listagem de vagas da Catho em Campinas/SP,
extrair os dados brutos de forma estruturada e retorná-los compatíveis com o modelo Job.
"""

import time
from typing import List, Dict, Any


class CathoScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.base_url = "https://www.catho.com.br"

    def scrape(self, keyword: str = "suporte ti", location: str = "Campinas", max_jobs: int = 10, page=None) -> List[Dict[str, Any]]:
        """
        Executa a varredura na Catho utilizando o BrowserManager oficial do projeto ou a página injetada.
        """
        from browser_utils import BrowserManager
        
        raw_jobs = []
        manager = None
        
        if not page:
            manager = BrowserManager(headless=self.headless)
            page = manager.start()

        try:
            formatted_kw = keyword.strip().replace(" ", "-")
            formatted_loc = location.strip().replace(" ", "-").lower()
            search_url = f"{self.base_url}/vagas/{formatted_kw}/-em-{formatted_loc}-sp/"
            
            print(f"[CATHO] Acessando {search_url}...")
            page.goto(search_url, timeout=30000)
            time.sleep(3)

            # Seletores de cards de vagas da Catho com múltiplos fallbacks
            card_selectors = [
                "article.sc-1b5e390-0",
                "div.job-card",
                "li[id*='job']",
                "article[class*='JobCard']",
                "div.sc-gzVnrw"
            ]

            cards = None
            for selector in card_selectors:
                try:
                    page.wait_for_selector(selector, timeout=4000)
                    found_cards = page.locator(selector).all()
                    if found_cards and len(found_cards) > 0:
                        cards = found_cards
                        print(f"[CATHO] Cards encontrados com o seletor: {selector} ({len(cards)} cards)")
                        break
                except Exception:
                    continue

            if not cards:
                print("[AVISO] Nenhum card de vaga encontrado na Catho com os seletores padrões.")
                if manager:
                    manager.close()
                return []

            for card in cards[:max_jobs]:
                try:
                    title_elem = card.locator("h2 a, a[data-gtm*='job'], h2 h3, a.sc-htoDjs").first
                    company_elem = card.locator("span[class*='company'], p[class*='company'], span.sc-dVhcbM").first
                    location_elem = card.locator("span[class*='location'], span.sc-fjdhpX").first
                    desc_elem = card.locator("p[class*='description'], div[class*='description']").first

                    title = title_elem.inner_text().strip() if title_elem.count() > 0 else ""
                    company = company_elem.inner_text().strip() if company_elem.count() > 0 else ""
                    location = location_elem.inner_text().strip() if location_elem.count() > 0 else ""
                    snippet = desc_elem.inner_text().strip() if desc_elem.count() > 0 else ""
                    
                    link = ""
                    if title_elem.count() > 0:
                        href = title_elem.get_attribute("href")
                        if href:
                            link = href if href.startswith("http") else f"{self.base_url}{href}"

                    if title:
                        raw_jobs.append({
                            "title": title,
                            "company": company or "Empresa não informada",
                            "location": location or "Campinas, SP",
                            "link": link or self.base_url,
                            "source": "Catho",
                            "description_snippet": snippet
                        })
                except Exception as inner_err:
                    print(f"[AVISO] Erro ao extrair card individual na Catho: {inner_err}")
                    continue

        except Exception as e:
            print(f"[ERRO] Falha geral ao acessar a Catho: {e}")
        finally:
            if manager:
                manager.close()

        print(f"[CATHO] Total de vagas brutas extraídas: {len(raw_jobs)}")
        return raw_jobs