from __future__ import annotations
import asyncio
import logging
import re
import urllib.parse
from typing import Any, Dict, List

logger = logging.getLogger("MAV-APINFO")

DEFAULT_SEARCH_TERMS = ["Python", "Java", "React", "Full Stack", "Suporte"]
BASE_URL = "https://www.apinfo.com/"


async def scrape_apinfo(page, terms: List[str] | None = None) -> List[Dict[str, Any]]:
    search_terms = terms or DEFAULT_SEARCH_TERMS
    all_jobs: List[Dict[str, Any]] = []
    seen_codes: set[str] = set()

    logger.info("[APINFO] Iniciando varredura para %d termos...", len(search_terms))

    for term in search_terms:
        try:
            await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(1000)

            input_selector = "input[type='text'], input[name='key'], input[name='palavra'], input[name='kw']"
            search_input = await page.query_selector(input_selector)

            if not search_input:
                logger.warning("[APINFO] Campo de busca não encontrado.")
                continue

            await search_input.fill(term)
            await search_input.press("Enter")
            await page.wait_for_timeout(2500)

            job_cards = await page.query_selector_all("div.box, table, div.vaga, .cargo")
            
            if not job_cards:
                continue

            for card in job_cards:
                try:
                    text_content = await card.inner_text()
                    if not text_content or len(text_content.strip()) < 30:
                        continue

                    lines = [line.strip() for line in text_content.split("\n") if line.strip()]
                    if not lines:
                        continue

                    # Extração do Código da Vaga
                    code_match = re.search(r"\[?(\d{4,6})\]?", text_content)
                    code = code_match.group(1) if code_match else "00000"

                    if code != "00000" and code in seen_codes:
                        continue

                    # Extração e Sanitização do Título (Cargo)
                    raw_title_line = lines[0]
                    for line in lines:
                        if any(k in line.lower() for k in ["cargo:", "vaga:", "desenvolvedor", "analista", "tecnico", "técnico", "engenheiro"]):
                            raw_title_line = line
                            break

                    # Remove código numérico [12345] ou "Código: 12345" do título
                    title = re.sub(r"\[?\d{4,6}\]?", "", raw_title_line)
                    title = re.sub(r"^(código|codigo|vaga|cargo)\s*:\s*", "", title, flags=re.IGNORECASE).strip()

                    # Caso a limpeza resulte em string vazia, utiliza fallback seguro
                    if not title or len(title) < 3:
                        title = f"Vaga {code}" if code != "00000" else "Profissional TI"

                    # Extração da Empresa e Localização
                    company = "Confidencial"
                    location = "Não informado"

                    for line in lines:
                        line_lower = line.lower()
                        if "local:" in line_lower or "região:" in line_lower or "uf:" in line_lower:
                            location = line.split(":", 1)[-1].strip()
                        elif "empresa:" in line_lower:
                            extracted_company = line.split(":", 1)[-1].strip()
                            if extracted_company:
                                company = extracted_company

                    link_elem = await card.query_selector("a[href*='cv'], a[href*='email'], a")
                    href = await link_elem.get_attribute("href") if link_elem else ""
                    
                    if href and not href.startswith("http"):
                        link = urllib.parse.urljoin("https://www.apinfo.com/", href)
                    else:
                        link = href or page.url

                    all_jobs.append({
                        "site": "ApInfo",
                        "title": title,
                        "company": company,
                        "location": location,
                        "code": code,
                        "search_term": term,
                        "link": link,
                        "raw_text": text_content[:600],
                    })

                    if code != "00000":
                        seen_codes.add(code)

                except Exception as card_err:
                    logger.debug("[APINFO] Erro ao processar cartão: %s", card_err)
                    continue

            await asyncio.sleep(0.5)

        except Exception as term_err:
            logger.error("[APINFO] Erro no termo '%s': %s", term, term_err)
            continue

    logger.info("[APINFO] Varredura finalizada. Total de vagas: %d", len(all_jobs))
    return all_jobs