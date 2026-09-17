"""
MAV — ETAPA 6.3: TESTE DE INTEGRAÇÃO DO PIPELINE COMPLETO
Valida o fluxo ponta a ponta: Normalização -> Deduplicação -> Matching.
"""

import unittest
from models import Job
from matcher import JobMatcher
from scrapers._helpers import process_scraped_pipeline


class TestPipelineIntegration(unittest.TestCase):

    def setUp(self):
        self.matcher = JobMatcher()

    def test_pipeline_normal_case(self):
        """TESTE 1 — Caso normal: processa vaga válida pelo pipeline completo."""
        job = Job(
            title="   Analista de Suporte Júnior   ",
            company=" Empresa Tech ",
            location="Campinas - SP",
            link="https://apinfo.com/vaga/pipe1",
            source="ApInfo",
            description_snippet="Suporte técnico N1 e N2, Windows 10, Active Directory e redes TCP/IP."
        )
        seen_ids = set()
        results = process_scraped_pipeline([job], seen_ids, self.matcher)
        
        self.assertEqual(len(results), 1)
        j_res, m_res = results[0]
        self.assertEqual(j_res.title, "Analista de Suporte Júnior")  # Normalizado (strip)
        self.assertGreaterEqual(m_res.score, 75.0)
        self.assertEqual(m_res.classification, "MUITO RELEVANTE")
        self.assertIn(j_res.unique_id(), seen_ids)

    def test_pipeline_incomplete_or_invalid_data(self):
        """TESTE 2 — Dados incompletos ou inválidos são tratados com segurança."""
        job_empty = Job(title="", company="", location="", link="", source="", description_snippet="")
        job_none = None
        
        seen_ids = set()
        results = process_scraped_pipeline([job_none, job_empty], seen_ids, self.matcher)
        self.assertEqual(len(results), 0)

    def test_pipeline_duplicate_batch_handling(self):
        """TESTE 3 — Lote com vagas duplicadas é deduplicado corretamente no pipeline."""
        job = Job(
            title="Analista de Infraestrutura",
            company="Cloud Corp",
            location="Campinas",
            link="https://apinfo.com/vaga/dup",
            source="ApInfo",
            description_snippet="Administração de servidores Linux Server, Ubuntu Server e redes locais."
        )
        seen_ids = set()
        # Envia a mesma vaga duplicada na lista
        results = process_scraped_pipeline([job, job], seen_ids, self.matcher)
        
        # Apenas uma deve passar pelo pipeline
        self.assertEqual(len(results), 1)
        self.assertEqual(len(seen_ids), 1)


if __name__ == "__main__":
    unittest.main()