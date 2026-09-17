"""
MAV — ETAPA 6.2: TESTE DE DEDUPLICAÇÃO E PERSISTÊNCIA
Valida o carregamento, salvamento e filtragem de vagas já vistas utilizando seen_jobs.json.
"""

import os
import unittest
from models import Job
from scrapers._helpers import load_seen_jobs, save_seen_jobs, filter_and_deduplicate


class TestDeduplicationAndPersistence(unittest.TestCase):

    def setUp(self):
        self.test_file = "test_seen_jobs_temp.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_01_load_empty_when_file_missing(self):
        """TESTE 1 — Carregar IDs quando o arquivo não existe retorna conjunto vazio."""
        seen = load_seen_jobs(self.test_file)
        self.assertEqual(seen, set())

    def test_02_save_and_load_seen_jobs(self):
        """TESTE 2 — Salvar e carregar IDs de vagas persistidos com sucesso."""
        sample_ids = {"hash123", "hash456", "hash789"}
        save_seen_jobs(sample_ids, self.test_file)
        
        loaded_ids = load_seen_jobs(self.test_file)
        self.assertEqual(loaded_ids, sample_ids)

    def test_03_filter_and_deduplicate_new_jobs(self):
        """TESTE 3 — Filtrar vagas novas e ignorar as que já estão no histórico."""
        job1 = Job(title="Analista de Suporte Júnior", company="Empresa A", location="Campinas", link="url1", source="ApInfo", description_snippet="suporte tecnico windows")
        job2 = Job(title="Analista de Infraestrutura", company="Empresa B", location="Campinas", link="url2", source="ApInfo", description_snippet="infraestrutura redes")
        
        seen_ids = set()
        
        # Primeira passada: ambas devem passar (desde que batam com as keywords padrão do config)
        first_batch = filter_and_deduplicate([job1, job2], seen_ids)
        self.assertEqual(len(first_batch), 2)
        self.assertEqual(len(seen_ids), 2)
        
        # Segunda passada com as mesmas vagas (já vistas): nenhuma deve passar
        second_batch = filter_and_deduplicate([job1, job2], seen_ids)
        self.assertEqual(len(second_batch), 0)

    def test_04_corrupted_json_handling(self):
        """TESTE 4 — Tratamento resiliente caso o arquivo JSON esteja corrompido."""
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("CONTEUDO_INVALIDO_NAO_JSON")
            
        seen = load_seen_jobs(self.test_file)
        self.assertEqual(seen, set())


if __name__ == "__main__":
    unittest.main()