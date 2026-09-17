"""
MAV — SCRAPER DO INDEED
Responsável por varrer as páginas de listagem de vagas do Indeed em Campinas/SP,
localizar os cards, extrair os dados brutos e retorná-los compatíveis com o modelo Job.
"""
import time
from typing import List, Dict, Any


class IndeedScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.base_url = "https://www.indeed.com.br"

    def scrape(self, keyword: str = "suporte ti", location: str = "Campinas, SP", max_jobs: int = 10, page=None) -> List[Dict[str, Any]]:
        """
        Executa a varredura no Indeed utilizando o BrowserManager oficial do projeto ou a página injetada.
        """
        from browser_utils import BrowserManager
        
        raw_jobs = []
        manager = None
        
        if not page:
            manager = BrowserManager(headless=self.headless)
            page = manager.start()

        try:
            formatted_kw = keyword.strip().replace(" ", "+")
            formatted_loc = location.strip().replace(" ", "+")
            search_url = f"{self.base_url}/jobs?q={formatted_kw}&l={formatted_loc}"
            
            print(f"[INDEED] Acessando {search_url}...")
            page.goto(search_url, timeout=30000)
            time.sleep(3)

            # Seletores de cards de vagas do Indeed com múltiplos fallbacks
            card_selectors = [
                "div.cardOutline",
                "div.job_seen_beacon",
                "td.resultContent",
                "div[class*='jobCard']",
                "li.css-5lfssm"
            ]

            cards = None
            for selector in card_selectors:
                try:
                    page.wait_for_selector(selector, timeout=4000)
                    found_cards = page.locator(selector).all()
                    if found_cards and len(found_cards) > 0:
                        cards = found_cards
                        print(f"[INDEED] Cards encontrados com o seletor: {selector} ({len(cards)} cards)")
                        break
                except Exception:
                    continue

            if not cards:
                print("[AVISO] Nenhum card de vaga encontrado no Indeed com os seletores padrões.")
                if manager:
                    manager.close()
                return []

            for card in cards[:max_jobs]:
                try:
                    title_elem = card.locator("h2.jobTitle span[title], a.jcs-JobTitle, span[id*='jobTitle']").first
                    company_elem = card.locator("span.companyName, [data-testid='company-name'], span.css-1f9apgn").first
                    location_elem = card.locator("div.companyLocation, [data-testid='text-location'], div.css-1p0sjhy").first
                    desc_elem = card.locator("div.job-snippet, div.css-1cvvo1b").first

                    title = title_elem.inner_text().strip() if title_elem.count() > 0 else ""
                    company = company_elem.inner_text().strip() if company_elem.count() > 0 else ""
                    location = location_elem.inner_text().strip() if location_elem.count() > 0 else ""
                    snippet = desc_elem.inner_text().strip() if desc_elem.count() > 0 else ""
                    
                    link = ""
                    link_elem = card.locator("a.jcs-JobTitle, h2.jobTitle a").first
                    if link_elem.count() > 0:
                        href = link_elem.get_attribute("href")
                        if href:
                            link = href if href.startswith("http") else f"{self.base_url}{href}"

                    if title:
                        raw_jobs.append({
                            "title": title,
                            "company": company or "Empresa não informada",
                            "location": location or "Campinas, SP",
                            "link": link or self.base_url,
                            "source": "Indeed",
                            "description_snippet": snippet
                        })
                except Exception as inner_err:
                    print(f"[AVISO] Erro ao extrair card individual no Indeed: {inner_err}")
                    continue

        except Exception as e:
            print(f"[ERRO] Falha geral ao acessar o Indeed: {e}")
        finally:
            if manager:
                manager.close()

        print(f"[INDEED] Total de vagas brutas extraídas: {len(raw_jobs)}")
        return raw_jobs