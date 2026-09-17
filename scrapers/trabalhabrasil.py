import re

async def trabalhabrasil_scraper(page):
    url = "https://www.trabalhabrasil.com.br/vagas-de-emprego/suporte-ti"

    # Evasão simples de detecção
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        window.chrome = { runtime: {} };
    """)

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=40000)

        # Loop de liberação do Cloudflare
        for attempt in range(1, 11):
            title = await page.title()
            if not any(term in title.lower() for term in ["just a moment", "atencao", "attention required"]):
                print(f"[TRABALHA BRASIL] Página liberada! Título: {title}")
                break
            print(f"[TRABALHA BRASIL] ⚠️ Desafio Cloudflare ativo (Tentativa {attempt}/10)...")
            await page.wait_for_timeout(2000)

        # Aguarda o script da página renderizar os elementos
        await page.wait_for_timeout(3000)

        # Scroll progressivo para forçar lazy-loading
        for offset in [500, 1200, 2000]:
            await page.evaluate(f"window.scrollTo(0, {offset});")
            await page.wait_for_timeout(600)

    except Exception as e:
        print(f"[TRABALHA BRASIL] Aviso no carregamento: {e}")

    # Aguarda seletores genéricos da estrutura de vagas
    try:
        await page.wait_for_selector("a[href*='vaga'], article, .job-card, div[class*='job']", timeout=10000)
    except Exception:
        print("[TRABALHA BRASIL] Alerta: Contêiner de vagas não detectado no tempo limite.")

    # Varredura completa de âncoras no DOM
    raw_vagas = await page.evaluate('''() => {
        const results = [];
        const anchors = Array.from(document.querySelectorAll("a[href]"));

        anchors.forEach(a => {
            const href = a.getAttribute("href") || "";
            const hrefLower = href.toLowerCase();
            
            // Captura qualquer link apontando para detalhes de vaga
            if (hrefLower.includes("/vaga-de-") || hrefLower.includes("/vaga/") || hrefLower.includes("vagas-de-emprego/")) {
                const card = a.closest("article, .job-card, .jg__card, div[class*='job'], div[class*='card']") || a.parentElement;
                
                results.push({
                    href: href,
                    title: a.innerText.trim(),
                    fullText: card ? card.innerText : a.innerText
                });
            }
        });
        return results;
    }''')

    vagas = []
    seen_links = set()

    for item in raw_vagas:
        link = item.get("href", "")
        if not link:
            continue

        clean_path = link.split("?")[0].split("#")[0].rstrip("/")
        
        # Filtra URLs institucionais ou da própria busca
        if clean_path.endswith("/vagas-de-emprego") or clean_path == "/vagas-de-emprego/suporte-ti":
            continue

        full_link = f"https://www.trabalhabrasil.com.br{clean_path}" if clean_path.startswith("/") else clean_path
        if full_link in seen_links:
            continue
        seen_links.add(full_link)

        # Extração de Título via Slug da URL
        title = ""
        match = re.search(r'/vaga-de-(.*?)(?:-em-|\/\d+|$)', clean_path, re.IGNORECASE)
        if match:
            slug_title = match.group(1).replace('emprego-de-', '').replace('-', ' ').strip()
            if slug_title:
                title = slug_title.title()

        if not title:
            raw_title = item.get("title", "").split("\n")[0].strip()
            if raw_title and not any(term in raw_title.lower() for term in ["vagas de emprego", "trabalha brasil", "buscar"]):
                title = raw_title

        if not title:
            continue

        vagas.append({
            "site": "TrabalhaBrasil",
            "title": title,
            "company": "Empresa Confidencial",
            "location": "Brasil",
            "link": full_link,
            "code": clean_path.split("/")[-1],
            "description": item.get("fullText", ""),  # Envia o texto do card para o Matcher
        })

    print(f"[TRABALHA BRASIL] Processamento finalizado: {len(vagas)} vagas extraídas.")
    return vagas

scrape_trabalhabrasil = trabalhabrasil_scraper