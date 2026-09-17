"""
MAV — TESTE DE INTEGRAÇÃO DO SCRAPER INFOJOBS
Valida a conversão de dados brutos do Infojobs para Job, 
resiliência e integração completa com o matcher.
"""

import unittest
from models import Job
from matcher import JobMatcher
from scrapers._helpers import process_scraped_pipeline


class TestInfojobsIntegration(unittest.TestCase):

    def setUp(self):
        self.matcher = JobMatcher()

    def test_01_parse_infojobs_raw_to_job(self):
        """TESTE 1 — Conversão correta de dados brutos do Infojobs para o modelo Job."""
        raw_data = {
            "title": "Analista de Suporte Técnico Pleno",
            "company": "Tech Campinas Ltda",
            "location": "Campinas, SP",
            "link": "https://www.infojobs.com.br/vaga-exemplo",
            "source": "Infojobs",
            "description_snippet": "Suporte a infraestrutura, redes TCP/IP, Active Directory e Python básico."
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

        self.assertEqual(job_norm.title, "Analista de Suporte Técnico Pleno")
        self.assertEqual(job_norm.company, "Tech Campinas Ltda")
        self.assertIn("redes", job_norm.description_snippet)
        self.assertEqual(job_norm.source, "Infojobs")

    def test_02_infojobs_matcher_pipeline(self):
        """TESTE 2 — Vaga do Infojobs passa corretamente pelo matcher analítico."""
        job = Job(
            title="Analista de Suporte e Infraestrutura de TI",
            company="Soluções Corporativas",
            location="Campinas - SP",
            link="https://infojobs.com.br/vaga/123",
            source="Infojobs",
            description_snippet="Suporte técnico em infraestrutura, redes TCP/IP, servidores Windows/Linux, Active Directory e automação com scripts em Python."
        )
        
        seen_ids = set()
        results = process_scraped_pipeline([job], seen_ids, self.matcher)

        self.assertEqual(len(results), 1)
        j_res, m_res = results[0]
        self.assertGreaterEqual(m_res.score, 75.0)
        self.assertIn(m_res.classification, ["MUITO RELEVANTE", "EXCELENTE"])

if __name__ == "__main__":
    unittest.main()