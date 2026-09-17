"""
MAV - Teste Manual do Matcher

Este arquivo serve para calibrar o matcher.py usando vagas reais
capturadas pelo scraper APInfo.

IMPORTANTE:
- Não acessa a internet.
- Não envia nada para o Discord.
- Não altera seen_jobs.json.
- Não altera o perfil.
- Apenas testa Job + PROFILE + Matcher.

Execução:

    python tests/test_matcher_manual.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# ============================================================
# GARANTE QUE A RAIZ DO PROJETO ESTEJA NO PYTHONPATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS DO MAV
# ============================================================

from models import Job
from matcher import match_job, print_match_result


# ============================================================
# VAGAS REAIS UTILIZADAS NO ÚLTIMO TESTE DO APINFO
# ============================================================

TEST_JOBS: list[Job] = [

    Job(
        title="Analista de Suporte Pleno",
        company="Oliver Network Tecnologia da Informação",
        location="Caieiras - SP - 27/08/26",
        link=(
            "https://www.apinfo.com/apinfo/inc/"
            "enviecv.cfm?codvaga=85465"
        ),
        source="ApInfo",
        description_snippet=(
            "Analista de Suporte Pleno. "
            "Atendimento e suporte técnico. "
            "Suporte a usuários, sistemas, redes, "
            "Windows, Microsoft, Active Directory, "
            "servidores, troubleshooting e infraestrutura."
        ),
    ),

    Job(
        title="ANALISTA DE CIBERSEGURANÇA",
        company="Ss3 tecnologia",
        location="Guarulhos - SP - 27/08/26",
        link=(
            "https://www.apinfo.com/apinfo/inc/"
            "enviecv.cfm?codvaga=85270"
        ),
        source="ApInfo",
        description_snippet=(
            "Atuação na área de segurança da informação, "
            "infraestrutura, redes e segurança de ambientes "
            "corporativos."
        ),
    ),

    Job(
        title="Analista de Dados PL",
        company="CAPITANI GROUP",
        location="Guarulhos - SP - 27/08/26",
        link=(
            "https://www.apinfo.com/apinfo/inc/"
            "enviecv.cfm?codvaga=85070"
        ),
        source="ApInfo",
        description_snippet=(
            "Atuação com análise de dados, indicadores, "
            "relatórios e ferramentas de dados."
        ),
    ),

    Job(
        title="ANALISTA DE INFRAESTRUTURA DE REDE SENIOR N3",
        company="Quality Technology",
        location="Guarulhos - SP - 27/08/26",
        link=(
            "https://www.apinfo.com/apinfo/inc/"
            "enviecv.cfm?codvaga=85102"
        ),
        source="ApInfo",
        description_snippet=(
            "Atuação com infraestrutura de redes, "
            "redes TCP/IP, servidores, suporte de infraestrutura, "
            "automação e ambientes corporativos."
        ),
    ),

    Job(
        title="Análise em Identidade Pleno - RBAC/SoD",
        company="Vitara Consultoria em Informática Ltda",
        location="Home Office - HO - 27/08/26",
        link=(
            "https://www.apinfo.com/apinfo/inc/"
            "enviecv.cfm?codvaga=86059"
        ),
        source="ApInfo",
        description_snippet=(
            "Atuação com gestão de identidade, RBAC, "
            "SoD, controles de acesso e governança."
        ),
    ),

    Job(
        title="Análise em Privacidade e GRC - Pleno",
        company="Vitara Consultoria em Informática Ltda",
        location="Home Office - HO - 27/08/26",
        link=(
            "https://www.apinfo.com/apinfo/inc/"
            "enviecv.cfm?codvaga=86058"
        ),
        source="ApInfo",
        description_snippet=(
            "Atuação com privacidade, governança, riscos, "
            "compliance e GRC."
        ),
    ),

    Job(
        title="Análise em Projetos - Júnior",
        company="Vitara Consultoria em Informática Ltda",
        location="Home Office - HO - 27/08/26",
        link=(
            "https://www.apinfo.com/apinfo/inc/"
            "enviecv.cfm?codvaga=85827"
        ),
        source="ApInfo",
        description_snippet=(
            "Atuação com projetos, acompanhamento de atividades, "
            "documentação e organização de projetos."
        ),
    ),

    Job(
        title="Analista de Desenvolvimento - Backend (.NET)",
        company="Alcateia Consulting",
        location="Home Office - HO - 27/08/26",
        link=(
            "https://www.apinfo.com/apinfo/inc/"
            "enviecv.cfm?codvaga=86046"
        ),
        source="ApInfo",
        description_snippet=(
            "Desenvolvimento backend utilizando .NET, "
            "programação, APIs, sistemas e banco de dados."
        ),
    ),
]


# ============================================================
# EXECUÇÃO DO TESTE
# ============================================================

def main() -> None:

    print()
    print("=" * 70)
    print("MAV — TESTE MANUAL DO MATCHER")
    print("=" * 70)

    print()
    print(f"Vagas para teste: {len(TEST_JOBS)}")

    print()
    print(
        "Estas vagas são utilizadas somente para calibrar "
        "o algoritmo de compatibilidade."
    )

    print()
    print("=" * 70)

    results = []

    # --------------------------------------------------------
    # Executa o matcher em cada vaga
    # --------------------------------------------------------

    for index, job in enumerate(TEST_JOBS, start=1):

        print()
        print(
            f"[TESTE {index}/{len(TEST_JOBS)}] "
            f"{job.title}"
        )

        try:

            result = match_job(job)

            results.append(result)

            print_match_result(result)

        except Exception as exc:

            print()
            print(
                f"[ERRO] Falha ao testar a vaga: {exc}"
            )

    # ========================================================
    # RESUMO
    # ========================================================

    print()
    print()
    print("=" * 70)
    print("RESUMO DA CALIBRAÇÃO")
    print("=" * 70)

    if not results:

        print()
        print("Nenhum resultado foi gerado.")
        return

    # --------------------------------------------------------
    # Ordena da maior para a menor compatibilidade
    # --------------------------------------------------------

    results.sort(
        key=lambda result: result.score,
        reverse=True,
    )

    print()

    for position, result in enumerate(results, start=1):

        status = (
            "✓ RELEVANTE"
            if result.is_relevant
            else "✗ NÃO RELEVANTE"
        )

        print(
            f"{position:02d}. "
            f"[{result.score:03d}/100] "
            f"{status:<15} "
            f"{result.job.title}"
        )

    # ========================================================
    # ESTATÍSTICAS
    # ========================================================

    relevant = [
        result
        for result in results
        if result.is_relevant
    ]

    scores = [
        result.score
        for result in results
    ]

    average_score = sum(scores) / len(scores)

    print()
    print("-" * 70)

    print(
        f"Vagas testadas:       {len(results)}"
    )

    print(
        f"Vagas relevantes:     {len(relevant)}"
    )

    print(
        f"Vagas descartadas:    "
        f"{len(results) - len(relevant)}"
    )

    print(
        f"Score médio:          "
        f"{average_score:.1f}/100"
    )

    print(
        f"Maior score:          "
        f"{max(scores)}/100"
    )

    print(
        f"Menor score:          "
        f"{min(scores)}/100"
    )

    print()
    print("=" * 70)
    print("TESTE CONCLUÍDO")
    print("=" * 70)
    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()