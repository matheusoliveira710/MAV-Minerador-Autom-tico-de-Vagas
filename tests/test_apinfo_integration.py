"""
MAV — TESTE DE INTEGRAÇÃO DO SCRAPER APINFO
Valida a conversão de dados brutos da ApInfo para Job, 
resiliência a campos ausentes e integração completa com o pipeline e matcher.
"""

import unittest
from models import Job
from matcher import JobMatcher
from scrapers._helpers import process_scraped_pipeline


class TestApInfoIntegration(unittest.TestCase):

    def setUp(self):
        self.matcher = JobMatcher()

    def test_01_parse_raw_data_to_job(self):
        """TESTE 1 — Conversão correta de dados brutos extraídos da ApInfo para o modelo Job."""
        raw_data = {
            "title": "Analista de Suporte Pleno",
            "company": "Oliver Network Tecnologia da Informação",
            "location": "Caieiras - SP",
            "link": "https://www.apinfo.com/vaga/detalhe?código=85465",
            "source": "ApInfo",
            "description_snippet": "Suporte técnico a usuários, Windows 10, redes TCP/IP e Active Directory."
        }

        job = Job(
            title=raw_data["title"],
            company=raw_data["company"],
            location=raw_data["location"],
            link=raw_data["link"],
            source=raw_data["source"],
            description_snippet=raw_data["description_snippet"]
        )

        job_norm = job.normalize()

        self.assertEqual(job_norm.title, "Analista de Suporte Pleno")
        self.assertEqual(job_norm.company, "Oliver Network Tecnologia da Informação")
        self.assertEqual(job_norm.location, "Caieiras - SP")
        self.assertIn("Windows 10", job_norm.description_snippet)
        self.assertEqual(job_norm.source, "ApInfo")
        self.assertTrue(job_norm.link.startswith("https://www.apinfo.com"))

    def test_02_scraper_to_matcher_integration(self):
        """TESTE 2 — Vaga extraída da ApInfo alimenta corretamente o Matcher e gera score válido."""
        job = Job(
            title="Analista de Suporte Júnior",
            company="Tech Solutions",
            location="Campinas - SP",
            link="https://apinfo.com/vaga/123",
            source="ApInfo",
            description_snippet="Atendimento a usuários, suporte técnico, manutenção de hardware e Active Directory."
        )
        
        seen_ids = set()
        results = process_scraped_pipeline([job], seen_ids, self.matcher)

        self.assertEqual(len(results), 1)
        j_res, m_res = results[0]
        self.assertGreaterEqual(m_res.score, 75.0)
        self.assertIn(m_res.classification, ["MUITO RELEVANTE", "EXCELENTE"])

    def test_03_incompatible_job_discarded(self):
        """TESTE 3 — Vaga incompatível (ex: Gerente Comercial) coletada é descartada pelas regras do matcher."""
        job = Job(
            title="Gerente Comercial Sênior",
            company="Vendas SA",
            location="Campinas - SP",
            link="https://apinfo.com/vaga/999",
            source="ApInfo",
            description_snippet="Gestão de equipe de vendas, prospecção de clientes e negociação B2B."
        )

        match_res = self.matcher.match(job)
        self.assertEqual(match_res.classification, "DESCARTAR")

    def test_04_missing_optional_fields_resilience(self):
        """TESTE 4 — Resiliência a dados com campos opcionais ausentes ou em branco."""
        job = Job(
            title="Suporte Técnico",
            company="",
            location="",
            link="",
            source="ApInfo",
            description_snippet=""
        )

        job_norm = job.normalize()
        self.assertEqual(job_norm.title, "Suporte Técnico")
        self.assertEqual(job_norm.company, "")
        self.assertEqual(job_norm.description_snippet, "")


if __name__ == "__main__":
    unittest.main()