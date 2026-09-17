async def vagas_scraper(page):
    url = "https://www.vagas.com.br/vagas-de-suporte-ti"
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)

    try:
        await page.wait_for_selector(".vaga", timeout=15000)
    except Exception as e:
        print(f"[VAGAS] Timeout aguardando elementos: {e}")
        return []

    cards = await page.query_selector_all(".vaga")
    vagas = []

    for card in cards:
        title_el = await card.query_selector("a.link-detalhes-vaga, h2.cargo")
        company_el = await card.query_selector(".empr, .empr-nome")
        location_el = await card.query_selector(".vaga-local")

        title = await title_el.inner_text() if title_el else ""
        company = await company_el.inner_text() if company_el else "Confidencial"
        location = await location_el.inner_text() if location_el else "Brasil"
        link = await title_el.get_attribute("href") if title_el else ""

        if title:
            vagas.append({
                "site": "Vagas",
                "title": title.strip(),
                "company": company.strip(),
                "location": location.strip(),
                "link": f"https://www.vagas.com.br{link}" if link.startswith("/") else link,
                "code": link.split("/")[-1] if link else str(hash(title.strip()))
            })

    return vagas

# Alias de compatibilidade
scrape_vagas = vagas_scraper