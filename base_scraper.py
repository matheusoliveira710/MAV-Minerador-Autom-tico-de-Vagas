from playwright.async_api import async_playwright
import asyncio
from utils.logger import setup_logger
from config import PLAYWRIGHT_CONFIG
import random

class BaseScraper:
    def __init__(self, platform_name):
        self.platform_name = platform_name
        self.logger = setup_logger(f'scraper.{platform_name}')
        
    async def init_browser(self):
        """Inicializa o browser com configurações anti-detecção"""
        self.playwright = await async_playwright().start()
        
        # Estratégias anti-bot
        self.browser = await self.playwright.chromium.launch(
            headless=PLAYWRIGHT_CONFIG['headless'],
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials'
            ]
        )
        
        self.context = await self.browser.new_context(
            viewport=PLAYWRIGHT_CONFIG['viewport'],
            user_agent=PLAYWRIGHT_CONFIG['user_agent'],
            java_script_enabled=True,
            ignore_https_errors=True
        )
        
        # Adiciona scripts para evitar detecção
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Remove trace de automação
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """)
        
        self.page = await self.context.new_page()
        
        # Adiciona delay aleatório entre ações
        self.page.set_default_timeout(30000)
        
    async def close_browser(self):
        """Fecha o browser"""
        if hasattr(self, 'browser'):
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
            
    async def random_delay(self, min_seconds=1, max_seconds=3):
        """Adiciona delay aleatório para simular comportamento humano"""
        await asyncio.sleep(random.uniform(min_seconds, max_seconds))
        
    async def safe_click(self, selector, retries=3):
        """Clique seguro com retry"""
        for attempt in range(retries):
            try:
                await self.page.wait_for_selector(selector, state='visible', timeout=10000)
                await self.page.click(selector)
                return True
            except Exception as e:
                self.logger.warning(f"Click failed (attempt {attempt+1}): {e}")
                await self.random_delay(1, 2)
        return False
        
    def filter_by_keywords(self, text, keywords):
        """Filtra texto por palavras-chave"""
        if not text:
            return False
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)
        
    async def scrape(self):
        """Método principal a ser implementado por cada plataforma"""
        raise NotImplementedError("Each scraper must implement scrape()")