"""
MAV — SCRAPER DO INFOJOBS
Responsável por varrer as páginas de listagem de vagas do Infojobs em Campinas/SP,
localizar os cards de vagas, extrair os dados brutos e retorná-los 
como instâncias brutas compatíveis com o modelo Job.
"""

import time
from typing import List, Dict, Any


class InfojobsScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.base_url = "https://www.infojobs.com.br"

    def scrape(self, keyword: str = "suporte ti", location: str = "Campinas", max_jobs: int = 10, page=None) -> List[Dict[str, Any]]:
        """
        Executa a varredura nas páginas de vagas do Infojobs utilizando o BrowserManager oficial ou a página injetada.
        """
        from browser_utils import BrowserManager
        
        raw_jobs = []
        manager = None
        
        if not page:
            manager = BrowserManager(headless=self.headless)
            page = manager.start()

        try:
            # Formata a keyword e a localização para a URL padrão do Infojobs
            formatted_keyword = keyword.strip().replace(" ", "-")
            formatted_location = location.strip().replace(" ", "-").lower()
            
            search_url = f"{self.base_url}/vagas-de-emprego-{formatted_keyword}-em-{formatted_location}.aspx"
            
            print(f"[INFOJOBS] Acessando {search_url}...")
            page.goto(search_url, timeout=30000)
            time.sleep(3)  # Aguarda carregamento inicial

            # Seletores comuns de cards de vagas no Infojobs
            card_selectors = [
                "div.js_jobItem",
                "div.card-job",
                "div[id*='job']",
                "li.box-vaga"
            ]

            cards = None
            for selector in card_selectors:
                try:
                    page.wait_for_selector(selector, timeout=4000)
                    found_cards = page.locator(selector).all()
                    if found_cards and len(found_cards) > 0:
                        cards = found_cards
                        print(f"[INFOJOBS] Cards encontrados com o seletor: {selector} ({len(cards)} cards)")
                        break
                except Exception:
                    continue

            if not cards:
                print("[AVISO] Nenhum card de vaga encontrado no Infojobs com os seletores padrões. Salvando diagnóstico...")
                try:
                    with open("infojobs_debug.html", "w", encoding="utf-8") as f:
                        f.write(page.content())
                    page.screenshot(path="infojobs_debug.png", full_page=True)
                    print("[INFOJOBS] Arquivos 'infojobs_debug.html' e 'infojobs_debug.png' salvos com sucesso.")
                except Exception as diag_err:
                    print(f"[AVISO] Falha ao salvar diagnóstico: {diag_err}")
                
                if manager:
                    manager.close()
                return []

            for card in cards[:max_jobs]:
                try:
                    title_elem = card.locator("h2 a, a.h2, a[class*='title'], h2").first
                    company_elem = card.locator("a[class*='company'], span[class*='company'], .text-muted").first
                    location_elem = card.locator("span[class*='location'], .text-sub, span[class*='city']").first
                    desc_elem = card.locator("div[class*='description'], p[class*='text']").first

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
                            "source": "Infojobs",
                            "description_snippet": snippet
                        })
                except Exception as inner_err:
                    print(f"[AVISO] Erro ao extrair card individual no Infojobs: {inner_err}")
                    continue

        except Exception as e:
            print(f"[ERRO] Falha geral ao acessar o Infojobs: {e}")
        finally:
            if manager:
                manager.close()

        print(f"[INFOJOBS] Total de vagas brutas extraídas: {len(raw_jobs)}")
        return raw_jobs