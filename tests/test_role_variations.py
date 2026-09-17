"""
MAV — TESTE DE VARIAÇÕES DE CARGOS

Etapa 1 do refinamento do Matcher.

Objetivo:
    Verificar se o Matcher reconhece corretamente diferentes
    formas de escrita dos cargos do perfil profissional.

Os testes utilizam o mesmo formato de objeto aceito pelo
JobMatcher.match() / match_job().
"""

from matcher import match_job

# ================================================================
# CASOS DE TESTE
# ================================================================

TEST_CASES = (

    # ------------------------------------------------------------
    # 🟢 SUPORTE — PRIORIDADE ALTA
    # ------------------------------------------------------------

    {
        "name": "Analista de Suporte Júnior",
        "job": {
            "title": "Analista de Suporte Júnior",
            "description": (
                "Atendimento aos usuários, troubleshooting, "
                "Windows e Active Directory."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 70,
        "expected_role": True,
    },

    {
        "name": "Analista de Suporte Junior",
        "job": {
            "title": "Analista de Suporte Junior",
            "description": (
                "Atendimento técnico N1 e N2 aos usuários."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 70,
        "expected_role": True,
    },

    {
        "name": "Analista de Suporte N1",
        "job": {
            "title": "Analista de Suporte N1",
            "description": (
                "Atendimento de chamados, suporte técnico "
                "e resolução de incidentes."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 60,
        "expected_role": True,
    },

    {
        "name": "Analista de Suporte N2",
        "job": {
            "title": "Analista de Suporte N2",
            "description": (
                "Suporte aos usuários, troubleshooting, "
                "Windows e redes."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 60,
        "expected_role": True,
    },

    {
        "name": "Técnico de Suporte",
        "job": {
            "title": "Técnico de Suporte",
            "description": (
                "Suporte técnico, manutenção de computadores "
                "e atendimento aos usuários."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 60,
        "expected_role": True,
    },

    {
        "name": "Tecnico de Suporte",
        "job": {
            "title": "Tecnico de Suporte",
            "description": (
                "Atendimento técnico, hardware, Windows e redes."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 60,
        "expected_role": True,
    },

    {
        "name": "Técnico de Informática",
        "job": {
            "title": "Técnico de Informática",
            "description": (
                "Manutenção de computadores, suporte aos usuários "
                "e redes."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 60,
        "expected_role": True,
    },

    {
        "name": "Suporte de TI",
        "job": {
            "title": "Suporte de TI",
            "description": (
                "Atendimento aos usuários, suporte técnico "
                "e infraestrutura."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 60,
        "expected_role": True,
    },

    {
        "name": "Service Desk",
        "job": {
            "title": "Analista de Service Desk",
            "description": (
                "Atendimento de chamados, suporte N1 "
                "e resolução de incidentes."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 60,
        "expected_role": True,
    },

    {
        "name": "Help Desk",
        "job": {
            "title": "Analista de Help Desk",
            "description": (
                "Suporte aos usuários, atendimento de chamados "
                "e troubleshooting."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 60,
        "expected_role": True,
    },

    # ------------------------------------------------------------
    # 🟢 INFRAESTRUTURA — PRIORIDADE ALTA
    # ------------------------------------------------------------

    {
        "name": "Analista de Infraestrutura",
        "job": {
            "title": "Analista de Infraestrutura",
            "description": (
                "Administração de servidores Linux, Windows, "
                "redes e Active Directory."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 70,
        "expected_role": True,
    },

    {
        "name": "Analista de Infraestrutura de TI",
        "job": {
            "title": "Analista de Infraestrutura de TI",
            "description": (
                "Servidores, redes, Windows, Linux "
                "e suporte aos usuários."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 70,
        "expected_role": True,
    },

    {
        "name": "Infraestrutura de TI",
        "job": {
            "title": "Analista de Infraestrutura de TI",
            "description": (
                "Infraestrutura, servidores Linux, redes "
                "e suporte técnico."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 65,
        "expected_role": True,
    },

    # ------------------------------------------------------------
    # 🟢 REDES — PRIORIDADE ALTA
    # ------------------------------------------------------------

    {
        "name": "Analista de Redes",
        "job": {
            "title": "Analista de Redes",
            "description": (
                "Administração de redes TCP/IP, LAN "
                "e infraestrutura."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 60,
        "expected_role": True,
    },

    # ------------------------------------------------------------
    # 🟡 SISTEMAS / ADMINISTRAÇÃO
    # ------------------------------------------------------------

    {
        "name": "Administrador de Redes",
        "job": {
            "title": "Administrador de Redes",
            "description": (
                "Administração de redes, servidores "
                "e infraestrutura."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 40,
        "expected_role": True,
    },

    {
        "name": "Administrador de Sistemas",
        "job": {
            "title": "Administrador de Sistemas",
            "description": (
                "Administração de servidores Linux, Windows "
                "e infraestrutura."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 40,
        "expected_role": True,
    },

    {
        "name": "SysAdmin",
        "job": {
            "title": "SysAdmin",
            "description": (
                "Administração de servidores Linux, redes "
                "e infraestrutura."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 35,
        "expected_role": True,
    },

    {
        "name": "Analista de Sistemas",
        "job": {
            "title": "Analista de Sistemas",
            "description": (
                "Suporte a sistemas corporativos, usuários "
                "e infraestrutura."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 40,
        "expected_role": True,
    },

    # ------------------------------------------------------------
    # 🟡 SEGURANÇA / DEVOPS
    # ------------------------------------------------------------

    {
        "name": "Analista de Segurança",
        "job": {
            "title": "Analista de Segurança da Informação",
            "description": (
                "Segurança da informação, infraestrutura, "
                "redes e sistemas."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 30,
        "expected_role": True,
    },

    {
        "name": "DevOps",
        "job": {
            "title": "Analista DevOps",
            "description": (
                "Automação, Linux, servidores, Git, "
                "Ansible e infraestrutura."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 30,
        "expected_role": True,
    },

    # ------------------------------------------------------------
    # 🔵 OPORTUNIDADES
    # ------------------------------------------------------------

    {
        "name": "Desenvolvedor Python Júnior",
        "job": {
            "title": "Desenvolvedor Python Júnior",
            "description": (
                "Desenvolvimento Python, scripts e automação."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 40,
        "expected_role": True,
    },

    {
        "name": "Desenvolvedor Python Junior",
        "job": {
            "title": "Desenvolvedor Python Junior",
            "description": (
                "Python, automação, scripts e Git."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 40,
        "expected_role": True,
    },

    {
        "name": "Desenvolvedor Backend",
        "job": {
            "title": "Desenvolvedor Backend",
            "description": (
                "Desenvolvimento backend utilizando Python, "
                "SQL e Git."
            ),
            "location": "Campinas - SP",
        },
        "min_score": 30,
        "expected_role": True,
    },

    # ------------------------------------------------------------
    # 🔴 FORA DO PERFIL
    # ------------------------------------------------------------

    {
        "name": "Gerente Comercial Sênior",
        "job": {
            "title": "Gerente Comercial Sênior",
            "description": (
                "Gestão de equipe comercial, vendas, "
                "metas e resultados."
            ),
            "location": "Campinas - SP",
        },
        "max_score": 20,
        "expected_role": False,
    },

    {
        "name": "Analista de Marketing",
        "job": {
            "title": "Analista de Marketing",
            "description": (
                "Marketing digital, campanhas, publicidade "
                "e redes sociais."
            ),
            "location": "Campinas - SP",
        },
        "max_score": 20,
        "expected_role": False,
    },

    {
        "name": "Vendedor",
        "job": {
            "title": "Vendedor",
            "description": (
                "Atendimento ao cliente, vendas e metas "
                "comerciais."
            ),
            "location": "Campinas - SP",
        },
        "max_score": 20,
        "expected_role": False,
    },
)


# ================================================================
# EXECUÇÃO DOS TESTES
# ================================================================

def run_tests() -> bool:
    """
    Executa todos os testes de variações de cargos.
    """

    print("=" * 70)
    print("MAV — ETAPA 1: TESTE DE VARIAÇÕES DE CARGOS")
    print("=" * 70)

    passed = 0
    failed = 0

    for index, test in enumerate(TEST_CASES, start=1):

        name = test["name"]
        job = test["job"]

        result = match_job(job)

        score = float(result.get("score", 0.0))
        classification = result.get(
            "classification",
            "N/A",
        )

        matched_roles = result.get(
            "matched_roles",
            [],
        )

        print()
        print(f"[{index:02d}] {name}")
        print(f"     Score: {score:.1f}")
        print(f"     Classificação: {classification}")

        if matched_roles:
            print(
                f"     Cargo reconhecido: "
                f"{matched_roles}"
            )
        else:
            print(
                "     Cargo reconhecido: nenhum"
            )

        test_passed = True

        # --------------------------------------------------------
        # Validação do cargo
        # --------------------------------------------------------

        expected_role = test.get(
            "expected_role",
            False,
        )

        if expected_role and not matched_roles:
            test_passed = False

            print(
                "     ❌ FALHOU — "
                "cargo esperado não foi reconhecido."
            )

        if not expected_role and matched_roles:
            test_passed = False

            print(
                "     ❌ FALHOU — "
                "cargo indevido foi reconhecido."
            )

        # --------------------------------------------------------
        # Score mínimo
        # --------------------------------------------------------

        if "min_score" in test:

            min_score = float(
                test["min_score"]
            )

            if score < min_score:
                test_passed = False

                print(
                    f"     ❌ FALHOU — "
                    f"score {score:.1f} < "
                    f"mínimo {min_score:.1f}"
                )

        # --------------------------------------------------------
        # Score máximo
        # --------------------------------------------------------

        if "max_score" in test:

            max_score = float(
                test["max_score"]
            )

            if score > max_score:
                test_passed = False

                print(
                    f"     ❌ FALHOU — "
                    f"score {score:.1f} > "
                    f"máximo {max_score:.1f}"
                )

        # --------------------------------------------------------
        # Resultado
        # --------------------------------------------------------

        if test_passed:
            passed += 1
            print("     ✅ PASSOU")
        else:
            failed += 1

    # ============================================================
    # RESUMO
    # ============================================================

    print()
    print("=" * 70)
    print("RESULTADO — ETAPA 1")
    print("=" * 70)

    print(
        f"Testes executados: {len(TEST_CASES)}"
    )

    print(
        f"Passaram:          {passed}"
    )

    print(
        f"Falharam:          {failed}"
    )

    if failed == 0:

        print()
        print(
            "✅ TODOS OS TESTES DE VARIAÇÕES "
            "DE CARGOS PASSARAM!"
        )

    else:

        print()
        print(
            "⚠️ Existem variações que precisam "
            "de ajuste no Matcher."
        )

    print("=" * 70)

    return failed == 0


# ================================================================
# EXECUÇÃO DIRETA
# ================================================================

if __name__ == "__main__":

    success = run_tests()

    if not success:
        raise SystemExit(1)
