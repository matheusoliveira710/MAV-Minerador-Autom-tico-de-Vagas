"""
MAV — TESTE DE INTEGRAÇÃO DO SCRAPER INDEED
Valida a conversão de dados brutos do Indeed para Job,
normalização e matching analítico.
"""

import unittest
from models import Job
from matcher import JobMatcher
from scrapers._helpers import process_scraped_pipeline


class TestIndeedIntegration(unittest.TestCase):

    def setUp(self):
        self.matcher = JobMatcher()

    def test_01_parse_indeed_raw_to_job(self):
        """TESTE 1 — Conversão correta de dados brutos do Indeed para o modelo Job."""
        raw_data = {
            "title": "Analista de Suporte de TI Pleno",
            "company": "Inova Campinas Tech",
            "location": "Campinas, SP",
            "link": "https://www.br.indeed.com/viewjob?jk=exemplo123",
            "source": "Indeed",
            "description_snippet": "Atendimento help desk, infraestrutura de redes, suporte a servidores Windows e Linux."
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

        self.assertEqual(job_norm.title, "Analista de Suporte de TI Pleno")
        self.assertEqual(job_norm.company, "Inova Campinas Tech")
        self.assertEqual(job_norm.source, "Indeed")
        self.assertIn("suporte", job_norm.description_snippet)

    def test_02_indeed_matcher_pipeline(self):
        """TESTE 2 — Vaga do Indeed passa corretamente pelo matcher analítico."""
        job = Job(
            title="Analista de Infraestrutura e Redes",
            company="Global IT Solutions",
            location="Campinas - SP",
            link="https://br.indeed.com/job/456",
            source="Indeed",
            description_snippet="Gerenciamento de redes TCP/IP, roteadores, suporte técnico corporativo e automação com Python."
        )
        
        seen_ids = set()
        results = process_scraped_pipeline([job], seen_ids, self.matcher)

        self.assertEqual(len(results), 1)
        j_res, m_res = results[0]
        self.assertGreaterEqual(m_res.score, 75.0)
        self.assertIn(m_res.classification, ["MUITO RELEVANTE", "EXCELENTE"])


if __name__ == "__main__":
    unittest.main()