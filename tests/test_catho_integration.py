"""
MAV — TESTE DE INTEGRAÇÃO DO SCRAPER CATHO
Valida a conversão de dados brutos da Catho para Job,
normalização e pipeline do matcher.
"""

import unittest
from models import Job
from matcher import JobMatcher
from scrapers._helpers import process_scraped_pipeline


class TestCathoIntegration(unittest.TestCase):

    def setUp(self):
        self.matcher = JobMatcher()

    def test_01_parse_catho_raw_to_job(self):
        """TESTE 1 — Conversão correta de dados brutos da Catho para o modelo Job."""
        raw_data = {
            "title": "Técnico de Suporte Operacional",
            "company": "Campinas Service TI",
            "location": "Campinas, SP",
            "link": "https://www.catho.com.br/vagas/exemplo",
            "source": "Catho",
            "description_snippet": "Suporte a microcomputadores, redes locais, impressoras e atendimento a usuários."
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

        self.assertEqual(job_norm.title, "Técnico de Suporte Operacional")
        self.assertEqual(job_norm.company, "Campinas Service TI")
        self.assertEqual(job_norm.source, "Catho")

    def test_02_catho_matcher_pipeline(self):
        """TESTE 2 — Vaga da Catho passa corretamente pelo matcher analítico."""
        job = Job(
            title="Analista de Suporte de TI",
            company="Redes & Infra Campinas",
            location="Campinas - SP",
            link="https://catho.com.br/vaga/789",
            source="Catho",
            description_snippet="Infraestrutura de TI, redes TCP/IP, suporte técnico, Active Directory e automação com scripts."
        )
        
        seen_ids = set()
        results = process_scraped_pipeline([job], seen_ids, self.matcher)

        self.assertEqual(len(results), 1)
        j_res, m_res = results[0]
        self.assertGreaterEqual(m_res.score, 75.0)
        self.assertIn(m_res.classification, ["MUITO RELEVANTE", "EXCELENTE"])


if __name__ == "__main__":
    unittest.main()