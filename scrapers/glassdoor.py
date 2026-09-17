"""
MAV — SCRAPER DO GLASSDOOR (VERSÃO ROBUSTA)
Responsável por varrer as vagas do Glassdoor com múltiplos seletores de fallback,
garantindo alta resiliência a mudanças de layout e classes dinâmicas.
"""

import time
from typing import List, Dict, Any


class GlassdoorScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.base_url = "https://www.glassdoor.com.br"

    def scrape(self, keyword: str = "suporte ti", location: str = "Campinas, SP", max_jobs: int = 10) -> List[Dict[str, Any]]:
        """
        Executa a varredura nas páginas de vagas do Glassdoor utilizando o BrowserManager oficial.
        """
        from browser_utils import BrowserManager
        
        raw_jobs = []
        manager = BrowserManager(headless=self.headless)
        page = manager.start()

        try:
            # URL de busca direta para Campinas / Suporte e Infraestrutura
            search_url = "https://www.glassdoor.com.br/Vagas/campinas-analista-de-suporte-vagas-SRCH_IL.0,9_IC=2531644_KO10,30.htm"
            
            print(f"[GLASSDOOR] Acessando {search_url}...")
            page.goto(search_url, timeout=30000)
            time.sleep(4)  # Aguarda a hidratação completa da página em React

            # Lista de seletores candidatos para os cards de vagas no Glassdoor atual
            card_selectors = [
                "li.react-job-listing",
                "div[data-test='job-card']",
                "article.jobCard",
                "div.jobCard",
                "li[id*='job-']",
                "div[class*='JobsList_jobListItem']"
            ]

            cards = None
            used_selector = ""

            for selector in card_selectors:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    found_cards = page.locator(selector).all()
                    if found_cards and len(found_cards) > 0:
                        cards = found_cards
                        used_selector = selector
                        print(f"[GLASSDOOR] Cards encontrados com o seletor: {selector} ({len(cards)} cards)")
                        break
                except Exception:
                    continue

            if not cards:
                print("[AVISO] Nenhum seletor padrão de cards do Glassdoor respondeu. Salvando diagnóstico visual...")
                try:
                    page.screenshot(path="glassdoor_debug.png", full_page=True)
                except Exception:
                    pass
                manager.close()
                return []

            for card in cards[:max_jobs]:
                try:
                    # Seletores internos robustos com múltiplos fallbacks
                    title_elem = card.locator("a[data-test='job-link'], a.jobLink, a[class*='jobTitle']").first
                    company_elem = card.locator("span[data-test='employer-short-name'], span[class*='EmployerName'], div[class*='companyName']").first
                    location_elem = card.locator("span[data-test='emp-location'], span[class*='Location']").first
                    desc_elem = card.locator("div[data-test='job-snippet'], div[class*='jobSnippet']").first

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
                            "link": link,
                            "source": "Glassdoor",
                            "description_snippet": snippet
                        })
                except Exception as inner_err:
                    print(f"[AVISO] Erro ao extrair card individual no Glassdoor: {inner_err}")
                    continue

        except Exception as e:
            print(f"[ERRO] Falha geral ao acessar o Glassdoor: {e}")
        finally:
            manager.close()

        print(f"[GLASSDOOR] Total de vagas brutas extraídas: {len(raw_jobs)}")
        return raw_jobs