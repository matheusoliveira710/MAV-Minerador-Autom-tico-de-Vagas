from __future__ import annotations
from .apinfo import scrape_apinfo
from .programathor import programathor_scraper
from .trabalhabrasil import trabalhabrasil_scraper
from .vagas import vagas_scraper

ALL_SCRAPERS = {
    "ApInfo": scrape_apinfo,
    "TrabalhaBrasil": trabalhabrasil_scraper,
    "Programathor": programathor_scraper,
    "Vagas": vagas_scraper,
}
