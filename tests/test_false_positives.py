"""
MAV — ETAPA 4: TESTE DE FALSOS POSITIVOS
Verifica se o matcher evita considerar vagas irrelevantes como relevantes 
apenas porque contêm termos genéricos de TI na descrição.
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


class TestFalsePositives(unittest.TestCase):

    def setUp(self):
        self.matcher = JobMatcher()

    def test_false_positive_cases(self):
        test_cases = [
            {
                "name": "Analista Administrativo — puro",
                "job": Job(
                    title="Analista Administrativo",
                    company="Empresa ABC",
                    location="Campinas - SP",
                    link="https://exemplo.com/fp/1",
                    source="ApInfo",
                    description_snippet="Rotinas administrativas, planilhas, controle de documentos e atendimento a clientes."
                ),
                "max_score": 30.0,
                "expected_classification": "DESCARTAR"
            },
            {
                "name": "Analista Financeiro — com termos de TI",
                "job": Job(
                    title="Analista Financeiro",
                    company="Banco XYZ",
                    location="Campinas",
                    link="https://exemplo.com/fp/2",
                    source="ApInfo",
                    description_snippet="Controle de fluxo de caixa, relatórios em Excel, utilização de sistemas corporativos, Windows e Microsoft 365, atendimento interno."
                ),
                "max_score": 40.0,
                "expected_classification": "BAIXA"
            },
            {
                "name": "Analista de Marketing",
                "job": Job(
                    title="Analista de Marketing",
                    company="Agência Digital",
                    location="Campinas",
                    link="https://exemplo.com/fp/3",
                    source="ApInfo",
                    description_snippet="Gestão de redes sociais, campanhas de marketing digital, criação de conteúdo e suporte a campanhas."
                ),
                "max_score": 30.0,
                "expected_classification": "DESCARTAR"
            },
            {
                "name": "Analista de RH",
                "job": Job(
                    title="Analista de Recursos Humanos",
                    company="Consultoria RH",
                    location="Campinas",
                    link="https://exemplo.com/fp/4",
                    source="ApInfo",
                    description_snippet="Recrutamento e seleção, folha de pagamento, atendimento a funcionários e suporte a processos de RH."
                ),
                "max_score": 30.0,
                "expected_classification": "DESCARTAR"
            },
            {
                "name": "Vendedor",
                "job": Job(
                    title="Vendedor",
                    company="Loja Varejo",
                    location="Campinas",
                    link="https://exemplo.com/fp/5",
                    source="ApInfo",
                    description_snippet="Vendas de balcão, atendimento ao cliente, metas comerciais."
                ),
                "max_score": 30.0,
                "expected_classification": "DESCARTAR"
            },
            {
                "name": "Gerente Comercial",
                "job": Job(
                    title="Gerente Comercial",
                    company="Comércio S.A.",
                    location="São Paulo",
                    link="https://exemplo.com/fp/6",
                    source="ApInfo",
                    description_snippet="Gestão de equipe comercial, vendas, contabilidade, financeiro e relatórios."
                ),
                "max_score": 30.0,
                "expected_classification": "DESCARTAR"
            },
            {
                "name": "Técnico de Segurança do Trabalho",
                "job": Job(
                    title="Técnico de Segurança do Trabalho",
                    company="Indústria Metalúrgica",
                    location="Campinas",
                    link="https://exemplo.com/fp/7",
                    source="ApInfo",
                    description_snippet="Elaboração de laudos, normas regulamentadoras (NRs), EPIs e inspeções de segurança industrial."
                ),
                "max_score": 40.0,
                "expected_classification": "BAIXA"
            },
            {
                "name": "Assistente Administrativo — engodo de TI",
                "job": Job(
                    title="Assistente Administrativo",
                    company="Escritório Contábil",
                    location="Campinas",
                    link="https://exemplo.com/fp/8",
                    source="ApInfo",
                    description_snippet="Suporte aos usuários internos, abertura de chamados, utilização de sistemas Windows, Microsoft Office e atendimento telefônico."
                ),
                "max_score": 45.0,
                "expected_classification": "BAIXA"
            },
            {
                "name": "Recepcionista",
                "job": Job(
                    title="Recepcionista",
                    company="Clínica Médica",
                    location="Campinas",
                    link="https://exemplo.com/fp/9",
                    source="ApInfo",
                    description_snippet="Recepção de pacientes, atendimento telefônico, agendamento de consultas e controle de acesso."
                ),
                "max_score": 30.0,
                "expected_classification": "DESCARTAR"
            },
            {
                "name": "Auxiliar Administrativo — armadilha de suporte",
                "job": Job(
                    title="Auxiliar Administrativo",
                    company="Empresa de Logística",
                    location="Campinas",
                    link="https://exemplo.com/fp/10",
                    source="ApInfo",
                    description_snippet="Arquivamento de documentos, planilhas Excel, atendimento técnico a rotinas administrativas e suporte operacional."
                ),
                "max_score": 45.0,
                "expected_classification": "BAIXA"
            },
        ]

        print("=" * 70)
        print("MAV — ETAPA 4: TESTE DE FALSOS POSITIVOS")
        print("=" * 70)

        failed_count = 0
        for idx, case in enumerate(test_cases, 1):
            res = self.matcher.match(case["job"])
            
            print(f"\n[{idx:02d}] {case['name']}")
            print(f"      Cargo: {case['job'].title}")
            print(f"      Score Obtido: {res.score}")
            print(f"      Classificação Obtida: {res.classification}")
            print(f"      Esperado Limite Máximo: <= {case['max_score']}")

            match_ok = True
            if res.score > case["max_score"]:
                match_ok = False

            if match_ok:
                print("      ✅ PASSOU")
            else:
                print("      ❌ FALHOU (Falso positivo detectado: score acima do limite)")
                failed_count += 1

        print("\n" + "=" * 70)
        print("RESULTADO — ETAPA 4")
        print("=" * 70)
        print(f"Testes executados: {len(test_cases)}")
        print(f"Passaram:          {len(test_cases) - failed_count}")
        print(f"Falharam:          {failed_count}")
        print("=" * 70)

        self.assertEqual(failed_count, 0, f"{failed_count} teste(s) de falsos positivos falharam.")


if __name__ == "__main__":
    unittest.main()
