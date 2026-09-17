"""
MAV — TESTE DE INTEGRAÇÃO DO SCRAPER GLASSDOOR
Valida a conversão de dados brutos do Glassdoor para Job, 
resiliência a campos ausentes e integração completa com o pipeline e matcher.
"""

import unittest
from models import Job
from matcher import JobMatcher
from scrapers._helpers import process_scraped_pipeline


class TestGlassdoorIntegration(unittest.TestCase):

    def setUp(self):
        self.matcher = JobMatcher()

    def test_01_parse_glassdoor_raw_to_job(self):
        """TESTE 1 — Conversão correta de dados brutos extraídos do Glassdoor para o modelo Job."""
        raw_data = {
            "title": "Técnico de Suporte de TI",
            "company": "Global Solutions Tech",
            "location": "Campinas, SP",
            "link": "https://www.glassdoor.com.br/vaga-exemplo",
            "source": "Glassdoor",
            "description_snippet": "Atendimento help desk, manutenção de computadores e redes locais."
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

        self.assertEqual(job_norm.title, "Técnico de Suporte de TI")
        self.assertEqual(job_norm.company, "Global Solutions Tech")
        self.assertEqual(job_norm.location, "Campinas, SP")
        self.assertIn("help desk", job_norm.description_snippet)
        self.assertEqual(job_norm.source, "Glassdoor")

    def test_02_glassdoor_to_matcher_pipeline(self):
        """TESTE 2 — Vaga extraída do Glassdoor passa corretamente pelo matcher e pipeline."""
        job = Job(
            title="Analista de Suporte Júnior",
            company="Inova Campinas",
            location="Campinas - SP",
            link="https://glassdoor.com.br/vaga/456",
            source="Glassdoor",
            description_snippet="Suporte técnico aos usuários, Windows 10 e Active Directory."
        )
        
        seen_ids = set()
        results = process_scraped_pipeline([job], seen_ids, self.matcher)

        self.assertEqual(len(results), 1)
        j_res, m_res = results[0]
        self.assertGreaterEqual(m_res.score, 75.0)
        self.assertIn(m_res.classification, ["MUITO RELEVANTE", "EXCELENTE"])

    def test_03_glassdoor_incompatible_job_discarded(self):
        """TESTE 3 — Vaga incompatível coletada do Glassdoor é descartada pelo pipeline."""
        job =Job(
            title="Consultor de Vendas Externas",
            company="Comércio Regional",
            location="Campinas - SP",
            link="https://glassdoor.com.br/vaga/789",
            source="Glassdoor",
            description_snippet="Prospecção de clientes e vendas corporativas."
        )

        match_res = self.matcher.match(job)
        self.assertEqual(match_res.classification, "DESCARTAR")

    def test_04_glassdoor_missing_fields_resilience(self):
        """TESTE 4 — Resiliência do modelo a campos opcionais ausentes no Glassdoor."""
        job = Job(
            title="Analista de Infraestrutura",
            company="",
            location="",
            link="",
            source="Glassdoor",
            description_snippet=""
        )

        job_norm = job.normalize()
        self.assertEqual(job_norm.title, "Analista de Infraestrutura")
        self.assertEqual(job_norm.company, "")


if __name__ == "__main__":
    unittest.main()