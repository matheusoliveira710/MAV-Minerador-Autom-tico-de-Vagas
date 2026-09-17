"""
MAV — ETAPA 3: TESTE DE INTEGRAÇÃO DO MATCHER
Testa o comportamento do matcher com vagas completas (cargo, empresa, local, descrição).
"""

import sys
import unittest
from dataclasses import dataclass

try:
    from models import Job
except ImportError:
    @dataclass
    class Job:
        title: str
        company: str
        location: str
        link: str
        source: str
        description_snippet: str = ""

from matcher import JobMatcher


class TestMatcherIntegration(unittest.TestCase):

    def setUp(self):
        self.matcher = JobMatcher()

    def test_integration_cases(self):
        test_cases = [
            {
                "name": "Analista de Suporte Júnior — vaga ideal",
                "job": Job(
                    title="Analista de Suporte Júnior",
                    company="Empresa Tech SP",
                    location="Campinas - SP",
                    link="https://exemplo.com/vaga/1",
                    source="ApInfo",
                    description_snippet="Suporte técnico N1 e N2, atendimento a usuários, Windows 10, Windows 11, Active Directory, redes TCP/IP, hardware, troubleshooting e backup. Vaga híbrida."
                ),
                "expected_classification": "MUITO RELEVANTE",
                "min_score": 85.0
            },
            {
                "name": "Analista de Suporte N1",
                "job": Job(
                    title="Analista de Suporte N1",
                    company="Suporte Global",
                    location="Campinas",
                    link="https://exemplo.com/vaga/2",
                    source="ApInfo",
                    description_snippet="Atendimento help desk, Service Desk, Windows, controle de chamados e suporte remoto."
                ),
                "expected_classification": "MUITO RELEVANTE",
                "min_score": 75.0
            },
            {
                "name": "Analista de Infraestrutura — vaga ideal",
                "job": Job(
                    title="Analista de Infraestrutura",
                    company="Infra Corp",
                    location="Campinas - SP",
                    link="https://exemplo.com/vaga/3",
                    source="ApInfo",
                    description_snippet="Administração de servidores Linux Server, Ubuntu Server, redes locais, backup, troubleshooting de infraestrutura de TI e VirtualBox."
                ),
                "expected_classification": "MUITO RELEVANTE",
                "min_score": 80.0
            },
            {
                "name": "Analista de Redes",
                "job": Job(
                    title="Analista de Redes",
                    company="Telecom SP",
                    location="Valinhos",
                    link="https://exemplo.com/vaga/4",
                    source="ApInfo",
                    description_snippet="Configuração de redes TCP/IP, roteadores, switches, infraestrutura de redes e suporte técnico."
                ),
                "expected_classification": "RELEVANTE",
                "min_score": 70.0
            },
            {
                "name": "Desenvolvedor Python Júnior",
                "job": Job(
                    title="Desenvolvedor Python Júnior",
                    company="Dev House",
                    location="Remoto",
                    link="https://exemplo.com/vaga/5",
                    source="ApInfo",
                    description_snippet="Desenvolvimento backend utilizando Python, automação com scripts, Git, SQL e MySQL."
                ),
                "expected_classification": "MODERADA",
                "min_score": 45.0
            },
            {
                "name": "Analista de Sistemas",
                "job": Job(
                    title="Analista de Sistemas",
                    company="Sistemas S.A.",
                    location="Hortolândia",
                    link="https://exemplo.com/vaga/6",
                    source="ApInfo",
                    description_snippet="Análise de sistemas corporativos, suporte a rotinas e banco de dados SQL."
                ),
                "expected_classification": "MODERADA",
                "min_score": 45.0
            },
            {
                "name": "Gerente Comercial — incompatível",
                "job": Job(
                    title="Gerente Comercial",
                    company="Comércio Varejista",
                    location="São Paulo - SP",
                    link="https://exemplo.com/vaga/7",
                    source="ApInfo",
                    description_snippet="Gestão de equipe de vendas, metas comerciais, contabilidade, financeiro e marketing."
                ),
                "expected_classification": "DESCARTAR",
                "max_score": 30.0
            },
            {
                "name": "Vendedor — incompatível",
                "job": Job(
                    title="Vendedor",
                    company="Loja de Roupas",
                    location="Campinas",
                    link="https://exemplo.com/vaga/8",
                    source="ApInfo",
                    description_snippet="Atendimento ao cliente em loja física, vendas de balcão e organização de vitrine."
                ),
                "expected_classification": "DESCARTAR",
                "max_score": 30.0
            },
        ]

        print("=" * 70)
        print("MAV — ETAPA 3: TESTE DE INTEGRAÇÃO DO MATCHER")
        print("=" * 70)

        failed_count = 0
        for idx, case in enumerate(test_cases, 1):
            res = self.matcher.match(case["job"])
            
            print(f"\n[{idx:02d}] {case['name']}")
            print(f"      Cargo: {case['job'].title}")
            print(f"      Esperado Classificação: {case['expected_classification']}")
            print(f"      Score Obtido: {res.score}")
            print(f"      Classificação Obtida: {res.classification}")

            match_ok = True
            if "expected_classification" in case:
                if res.classification != case["expected_classification"]:
                    match_ok = False
            if "min_score" in case:
                if res.score < case["min_score"]:
                    match_ok = False
            if "max_score" in case:
                if res.score > case["max_score"]:
                    match_ok = False

            if match_ok:
                print("      ✅ PASSOU")
            else:
                print("      ❌ FALHOU")
                failed_count += 1

        print("\n" + "=" * 70)
        print("RESULTADO — ETAPA 3")
        print("=" * 70)
        print(f"Testes executados: {len(test_cases)}")
        print(f"Passaram:          {len(test_cases) - failed_count}")
        print(f"Falharam:          {failed_count}")
        print("=" * 70)

        self.assertEqual(failed_count, 0, f"{failed_count} teste(s) de integração falharam.")


if __name__ == "__main__":
    unittest.main()