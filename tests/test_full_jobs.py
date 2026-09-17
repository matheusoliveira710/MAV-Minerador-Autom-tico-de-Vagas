"""
MAV — ETAPA 5: TESTE DE VAGAS COMPLETAS
Valida o comportamento do matcher utilizando cenários realistas de vagas completas 
(cargo, empresa, localização, descrição detalhada e requisitos técnicos).
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


class TestFullJobsIntegration(unittest.TestCase):

    def setUp(self):
        self.matcher = JobMatcher()

    def test_full_jobs_scenarios(self):
        test_cases = [
            {
                "name": "01 — Vaga ideal de Suporte",
                "job": Job(
                    title="Analista de Suporte Júnior",
                    company="TechCorp Soluções",
                    location="Campinas - SP",
                    link="https://exemplo.com/vaga/full/1",
                    source="ApInfo",
                    description_snippet="Buscamos Analista de Suporte Júnior para atuação em suporte técnico N1 e N2, atendimento de usuários, troubleshooting de computadores, notebooks e periféricos, gerenciamento de contas de usuário via Active Directory e suporte a redes locais. Necessário conhecimento em Windows 10 e Windows 11, além de manutenção de hardware e abertura de chamados."
                ),
                "expected_classification": "MUITO RELEVANTE",
                "min_score": 80.0
            },
            {
                "name": "02 — Vaga ideal de Infraestrutura",
                "job": Job(
                    title="Analista de Infraestrutura",
                    company="InfraCloud Ltda",
                    location="Campinas",
                    link="https://exemplo.com/vaga/full/2",
                    source="ApInfo",
                    description_snippet="Profissional focado em administração de servidores Linux Server e Ubuntu Server, redes TCP/IP, infraestrutura de redes corporativas, rotinas de backup, virtualização com VirtualBox e máquinas virtuais. Experiência sólida com infraestrutura de TI, Active Directory e resolução de incidentes complexos."
                ),
                "expected_classification": "EXCELENTE",
                "min_score": 90.0
            },
            {
                "name": "03 — Suporte N1",
                "job": Job(
                    title="Analista de Suporte N1",
                    company="HelpDesk Global",
                    location="Hortolândia",
                    link="https://exemplo.com/vaga/full/3",
                    source="ApInfo",
                    description_snippet="Atendimento ao usuário final, abertura e gestão de chamados em service desk, suporte remoto via TeamViewer, solução de problemas em sistemas Windows, suporte técnico básico de hardware e periféricos."
                ),
                "expected_classification": "MUITO RELEVANTE",
                "min_score": 75.0
            },
            {
                "name": "04 — Redes",
                "job": Job(
                    title="Analista de Redes",
                    company="Conecta Telecom",
                    location="Valinhos",
                    link="https://exemplo.com/vaga/full/4",
                    source="ApInfo",
                    description_snippet="Configuração e monitoramento de redes TCP/IP, redes locais LAN, switches, roteadores, infraestrutura de redes, troubleshooting de conectividade e suporte a servidores locais."
                ),
                "expected_classification": "MUITO RELEVANTE",
                "min_score": 70.0
            },
            {
                "name": "05 — Desenvolvimento Python",
                "job": Job(
                    title="Desenvolvedor Python Júnior",
                    company="CodeSoft Inovação",
                    location="Remoto",
                    link="https://exemplo.com/vaga/full/5",
                    source="ApInfo",
                    description_snippet="Desenvolvimento backend utilizando Python, construção de APIs, versionamento de código com Git e GitHub, integração com banco de dados SQL e MySQL, além de automação de tarefas por meio de scripts."
                ),
                "expected_classification": "MODERADA",
                "min_score": 45.0
            },
            {
                "name": "06 — Analista de Sistemas",
                "job": Job(
                    title="Analista de Sistemas",
                    company="Sistemas Corporativos S.A.",
                    location="Campinas - SP",
                    link="https://exemplo.com/vaga/full/6",
                    source="ApInfo",
                    description_snippet="Levantamento de requisitos de software, análise funcional de sistemas, documentação de processos, integração com bancos de dados SQL e suporte a rotinas corporativas."
                ),
                "expected_classification": "MODERADA",
                "min_score": 45.0
            },
            {
                "name": "07 — Cargo incompatível com muitos termos de TI",
                "job": Job(
                    title="Analista Financeiro",
                    company="Banco de Investimentos",
                    location="São Paulo - SP",
                    link="https://exemplo.com/vaga/full/7",
                    source="ApInfo",
                    description_snippet="Gestão de fluxo de caixa, relatórios financeiros avançados em Excel, controle orçamentário. O profissional utilizará computadores, sistemas corporativos e software de gestão integrado, prestando atendimento interno financeiro."
                ),
                "expected_classification": "DESCARTAR",
                "max_score": 30.0
            },
            {
                "name": "08 — Administrativo com suporte",
                "job": Job(
                    title="Assistente Administrativo",
                    company="Escritório Contábil",
                    location="Sumaré",
                    link="https://exemplo.com/vaga/full/8",
                    source="ApInfo",
                    description_snippet="Atendimento interno a clientes e fornecedores, organização de documentos físicos e digitais, planilhas Excel, suporte administrativo à diretoria e abertura de chamados administrativos."
                ),
                "expected_classification": "DESCARTAR",
                "max_score": 30.0
            },
            {
                "name": "09 — Vaga comercial",
                "job": Job(
                    title="Gerente Comercial",
                    company="Varejo Paulista",
                    location="Campinas",
                    link="https://exemplo.com/vaga/full/9",
                    source="ApInfo",
                    description_snippet="Gestão de equipe de vendas, prospecção de clientes, fechamento de contratos, cumprimento de metas comerciais agressivas, negociação de preços e utilização de CRM."
                ),
                "expected_classification": "DESCARTAR",
                "max_score": 30.0
            },
            {
                "name": "10 — Vaga híbrida",
                "job": Job(
                    title="Analista de Suporte Júnior",
                    company="DevOps & Support Solutions",
                    location="Campinas - SP",
                    link="https://exemplo.com/vaga/full/10",
                    source="ApInfo",
                    description_snippet="Vaga híbrida de suporte e infraestrutura. Atuação com Linux, servidores, redes TCP/IP, automação de tarefas utilizando Python e scripts Ansible, gerenciamento de máquinas virtuais e suporte técnico a usuários."
                ),
                "expected_classification": "EXCELENTE",
                "min_score": 90.0
            },
        ]

        print("=" * 75)
        print("MAV — ETAPA 5: TESTE DE VAGAS COMPLETAS")
        print("=" * 75)

        failed_count = 0
        for idx, case in enumerate(test_cases, 1):
            res = self.matcher.match(case["job"])
            
            print(f"\n[{idx:02d}] {case['name']}")
            print(f"     Cargo: {case['job'].title}")
            print(f"     Score Obtido: {res.score:.1f}")
            print(f"     Classificação Obtida: {res.classification}")
            print(f"     Esperado: {case['expected_classification']}")
            print(f"     Cargo reconhecido: {res.matched_roles}")
            print(f"     Core Skills: {res.matched_core_skills[:4]}...")

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
                print("\n     ✅ PASSOU")
            else:
                print("\n     ❌ FALHOU")
                failed_count += 1

        print("\n" + "=" * 75)
        print("RESULTADO — ETAPA 5")
        print("=" * 75)
        print(f"Testes executados: {len(test_cases)}")
        print(f"Passaram:          {len(test_cases) - failed_count}")
        print(f"Falharam:          {failed_count}")
        print("=" * 75)

        self.assertEqual(failed_count, 0, f"{failed_count} teste(s) de vagas completas falharam.")


if __name__ == "__main__":
    unittest.main()