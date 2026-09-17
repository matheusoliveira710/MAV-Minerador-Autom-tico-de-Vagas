from models import Job


# ============================================================
# MOCK DE KEYWORDS
# ============================================================

KEYWORDS = {

    "Suporte": [
        "suporte técnico",
        "service desk",
    ],

    "Infraestrutura": [
        "infraestrutura",
        "windows",
    ],

    "Redes": [
        "tcp/ip",
        "redes",
    ],

    "Microsoft / AD": [
        "active directory",
    ],

    "Desenvolvimento": [
        "python",
    ],
}


# ============================================================
# PESOS
# ============================================================

WEIGHTS = {

    "Suporte": 5,

    "Infraestrutura": 5,

    "Redes": 4,

    "Microsoft / AD": 4,

    "Desenvolvimento": 1,
}


# ============================================================
# TESTE DE COMPATIBILIDADE
# ============================================================

def test_job_matches_resume_profile():

    job = Job(

        title=(
            "Analista de "
            "Suporte Júnior"
        ),

        company=(
            "Empresa Teste"
        ),

        location=(
            "Campinas - SP"
        ),

        link=(
            "https://example.com/"
            "vaga/123"
        ),

        source="APInfo",

        description_snippet=(

            "Atendimento N1, "
            "Windows, "
            "Active Directory, "
            "TCP/IP e "
            "troubleshooting."
        ),
    )

    result = job.matches_keywords(

        KEYWORDS,

        [],

        WEIGHTS,

        minimum_score=5,
    )

    assert result is True

    assert job.score >= 5

    assert (
        "Infraestrutura"
        in job.matched_categories
    )


# ============================================================
# TESTE DE EXCLUSÃO
# ============================================================

def test_excluded_job_does_not_match():

    job = Job(

        title=(
            "Gerente de TI"
        ),

        company=(
            "Empresa Teste"
        ),

        location=(
            "São Paulo - SP"
        ),

        link=(
            "https://example.com/"
            "vaga/456"
        ),

        source="APInfo",

        description_snippet=(
            "Gestão de equipe "
            "e infraestrutura."
        ),
    )

    result = job.matches_keywords(

        KEYWORDS,

        [
            "gerente de ti"
        ],

        WEIGHTS,

        minimum_score=5,
    )

    assert result is False


# ============================================================
# TESTE DE HASH
# ============================================================

def test_unique_id_is_stable():

    job = Job(

        title="Analista",

        company="Empresa",

        location="Campinas",

        link=(
            "https://example.com/"
            "vaga/1"
        ),

        source="APInfo",
    )

    first_id = (
        job.unique_id()
    )

    second_id = (
        job.unique_id()
    )

    assert first_id == second_id

    assert len(first_id) == 64
