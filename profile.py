from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProfessionalProfile:
    name: str = "Matheus Correia de Oliveira"

    target_roles: tuple[str, ...] = (
        "Analista de Suporte Júnior",
        "Analista de Suporte",
        "Suporte de TI",
        "Técnico de Suporte",
        "Técnico de Informática",
        "Analista de Infraestrutura",
        "Analista de Infraestrutura de TI",
        "Infraestrutura de TI",
        "Analista de Redes",
        "Analista de Sistemas",
        "Service Desk",
        "Help Desk",
    )

    secondary_roles: tuple[str, ...] = (
        "Administrador de Redes",
        "Administrador de Sistemas",
        "Administrador de Infraestrutura",
        "SysAdmin",
        "Analista de Segurança",
        "Segurança da Informação",
        "Analista de Cibersegurança",
        "DevOps",
        "Cloud",
        "Analista de Cloud",
        "Analista de Operações de TI",
    )

    opportunity_roles: tuple[str, ...] = (
        "Desenvolvedor Júnior",
        "Desenvolvedor Junior",
        "Desenvolvedor Python",
        "Desenvolvedor",
        "Analista de Desenvolvimento",
        "Desenvolvedor Backend",
        "Desenvolvedor Back-end",
        "Backend",
        "Back-end",
        "DBA",
        "Analista de Banco de Dados",
    )

    primary_areas: tuple[str, ...] = (
        "Suporte de TI",
        "Infraestrutura de TI",
        "Service Desk",
        "Redes",
        "Sistemas",
    )

    secondary_areas: tuple[str, ...] = (
        "Segurança da Informação",
        "Cibersegurança",
        "Administração de Redes",
        "Administração de Sistemas",
        "SysAdmin",
        "DevOps",
        "Automação",
        "Cloud Computing",
        "Virtualização",
    )

    core_skills: tuple[str, ...] = (
        "suporte técnico",
        "suporte de ti",
        "help desk",
        "helpdesk",
        "service desk",
        "atendimento técnico",
        "suporte n1",
        "suporte n2",
        "n1",
        "n2",
        "troubleshooting",
        "resolução de incidentes",
        "gestão de chamados",
        "tickets",
        "windows",
        "windows 10",
        "windows 11",
        "linux",
        "ubuntu",
        "ubuntu server",
        "redes",
        "rede",
        "redes tcp/ip",
        "tcp/ip",
        "infraestrutura de redes",
        "rede local",
        "lan",
        "active directory",
        "administração de usuários",
        "usuários",
        "contas de usuário",
        "hardware",
        "manutenção de hardware",
        "computadores",
        "notebooks",
        "periféricos",
        "microsoft 365",
        "office 365",
        "servidores",
        "servidor",
        "administração de servidores",
        "linux server",
        "backup",
        "acesso remoto",
        "suporte remoto",
    )

    complementary_skills: tuple[str, ...] = (
        "virtualbox",
        "virtualização",
        "virtualizacao",
        "máquinas virtuais",
        "vm",
        "vms",
        "python",
        "automação",
        "automacao",
        "scripts",
        "ansible",
        "playbooks",
        "git",
        "github",
        "controle de versão",
        "controle de versao",
        "javascript",
        "html",
        "html5",
        "css",
        "css3",
        "react",
        "sql",
        "mysql",
        "cloud",
        "cloud computing",
        "computação em nuvem",
        "computacao em nuvem",
        "segurança",
        "seguranca",
        "segurança da informação",
        "seguranca da informacao",
        "teamviewer",
    )

    technical_skills: dict[str, tuple[str, ...]] = field(
        default_factory=lambda: {
            "suporte": (
                "suporte técnico",
                "suporte de ti",
                "help desk",
                "helpdesk",
                "service desk",
                "atendimento técnico",
                "suporte n1",
                "suporte n2",
                "n1",
                "n2",
                "troubleshooting",
                "resolução de incidentes",
                "gestão de chamados",
                "tickets",
            ),
            "sistemas_operacionais": (
                "windows",
                "windows 10",
                "windows 11",
                "linux",
                "ubuntu",
                "ubuntu server",
                "linux server",
            ),
            "redes": (
                "redes",
                "rede",
                "redes tcp/ip",
                "tcp/ip",
                "infraestrutura de redes",
                "rede local",
                "lan",
            ),
            "identidade": (
                "active directory",
                "administração de usuários",
                "usuários",
                "contas de usuário",
            ),
            "hardware": (
                "hardware",
                "manutenção de hardware",
                "computadores",
                "notebooks",
                "periféricos",
            ),
            "microsoft": (
                "microsoft 365",
                "office 365",
            ),
            "acesso_remoto": (
                "acesso remoto",
                "suporte remoto",
                "teamviewer",
            ),
            "virtualizacao": (
                "virtualbox",
                "virtualização",
                "virtualizacao",
                "máquinas virtuais",
                "vm",
                "vms",
            ),
            "servidores": (
                "servidores",
                "servidor",
                "administração de servidores",
                "backup",
            ),
            "desenvolvimento": (
                "python",
                "javascript",
                "html",
                "html5",
                "css",
                "css3",
                "react",
                "sql",
                "mysql",
            ),
            "automacao": (
                "automação",
                "automacao",
                "scripts",
                "ansible",
                "playbooks",
            ),
            "versionamento": (
                "git",
                "github",
                "controle de versão",
                "controle de versao",
            ),
            "seguranca": (
                "segurança",
                "seguranca",
                "segurança da informação",
                "seguranca da informacao",
            ),
            "cloud": (
                "cloud",
                "cloud computing",
                "computação em nuvem",
                "computacao em nuvem",
            ),
        }
    )

    experience: tuple[dict[str, any], ...] = field(
        default_factory=lambda: (
            {
                "company": "Embrapa Agricultura Digital",
                "role": "Estagiário de Suporte de TI",
                "level": "N1/N2",
                "period": "09/2024 - 09/2025",
                "skills": (
                    "Service Desk",
                    "Suporte N1",
                    "Suporte N2",
                    "Windows",
                    "Linux",
                    "Redes TCP/IP",
                    "Active Directory",
                    "Hardware",
                    "Troubleshooting",
                    "Backup",
                    "Sistemas corporativos",
                ),
            },
            {
                "company": "Supermercados Pague Menos",
                "role": "Operador de Caixa / Atendimento",
                "period": "12/2025 - Atual",
                "skills": (
                    "Atendimento",
                    "Sistemas de automação comercial",
                    "PDV",
                    "Suporte técnico de primeiro nível",
                ),
            },
        )
    )

    projects: tuple[str, ...] = (
        "Automação e Infraestrutura",
        "Ansible",
        "Scripts de automação",
        "Servidores Linux",
        "Ubuntu Server",
        "Virtualização",
        "VirtualBox",
        "Monitoramento",
        "Bots",
        "Discord",
        "Telegram",
        "Cloud Computing",
        "Desenvolvimento Web",
    )

    education: tuple[dict[str, str], ...] = field(
        default_factory=lambda: (
            {
                "course": "Análise e Desenvolvimento de Sistemas",
                "institution": "Unimetrocamp Wyden",
                "status": "Cursando",
                "expected_completion": "Dezembro de 2027",
            },
            {
                "course": "Ensino Médio",
                "institution": "Colégio Adventista de Campinas",
                "status": "Concluído",
                "completion": "2021",
            },
        )
    )

    location: str = "Campinas - SP"

    preferred_locations: tuple[str, ...] = (
        "Campinas",
        "Campinas - SP",
    )

    regional_locations: tuple[str, ...] = (
        "Campinas",
        "Campinas - SP",
        "Valinhos",
        "Vinhedo",
        "Hortolândia",
        "Sumaré",
        "Paulínia",
        "Indaiatuba",
        "Jundiaí",
    )

    preferred_work_modes: tuple[str, ...] = (
        "home office",
        "home-office",
        "remoto",
        "remota",
        "híbrido",
        "hibrido",
        "presencial",
    )

    experience_level: tuple[str, ...] = (
        "júnior",
        "junior",
    )

    preferred_levels: tuple[str, ...] = (
        "estágio",
        "estagio",
        "júnior",
        "junior",
    )

    acceptable_levels: tuple[str, ...] = (
        "pleno",
        "plena",
    )

    avoid_levels: tuple[str, ...] = (
        "sênior",
        "senior",
        "especialista",
        "coordenador",
        "coordenadora",
        "gerente",
        "gerência",
        "gerencia",
        "supervisor",
        "supervisora",
        "diretor",
        "diretora",
    )

    priority_keywords: tuple[str, ...] = (
        "suporte",
        "suporte técnico",
        "suporte de ti",
        "service desk",
        "help desk",
        "infraestrutura",
        "infraestrutura de ti",
        "redes",
        "infraestrutura de redes",
        "tcp/ip",
        "windows",
        "linux",
        "ubuntu",
        "active directory",
        "hardware",
        "troubleshooting",
        "servidores",
        "backup",
        "microsoft 365",
    )

    secondary_keywords: tuple[str, ...] = (
        "python",
        "ansible",
        "automação",
        "automacao",
        "scripts",
        "virtualbox",
        "virtualização",
        "virtualizacao",
        "git",
        "github",
        "cloud",
        "cloud computing",
        "sql",
        "mysql",
        "javascript",
        "react",
        "segurança",
        "seguranca",
        "cibersegurança",
        "ciberseguranca",
    )

    high_priority_roles: tuple[str, ...] = (
        "analista de suporte júnior",
        "analista de suporte junior",
        "analista de suporte",
        "suporte de ti",
        "técnico de suporte",
        "tecnico de suporte",
        "técnico de informática",
        "tecnico de informatica",
        "analista de infraestrutura",
        "analista de infraestrutura de ti",
        "infraestrutura de ti",
        "analista de redes",
        "analista de sistemas",
        "service desk",
        "help desk",
    )

    secondary_roles_keywords: tuple[str, ...] = (
        "administrador de redes",
        "administrador de sistemas",
        "administrador de infraestrutura",
        "sysadmin",
        "analista de segurança",
        "analista de seguranca",
        "segurança da informação",
        "seguranca da informacao",
        "analista de cibersegurança",
        "analista de ciberseguranca",
        "devops",
        "cloud",
        "analista de cloud",
        "analista de operações de ti",
        "analista de operacoes de ti",
    )

    opportunity_roles_keywords: tuple[str, ...] = (
        "desenvolvedor júnior",
        "desenvolvedor junior",
        "desenvolvedor python",
        "desenvolvedor",
        "analista de desenvolvimento",
        "desenvolvedor backend",
        "desenvolvedor back-end",
        "backend",
        "back-end",
        "dba",
        "analista de banco de dados",
    )

    low_relevance_keywords: tuple[str, ...] = (
        "vendas",
        "vendedor",
        "comercial",
        "marketing",
        "contabilidade",
        "financeiro",
        "jurídico",
        "juridico",
        "rh",
        "recursos humanos",
        "secretária",
        "secretaria",
        "telemarketing",
    )


# Instância global do perfil para importação pelo Matcher
PROFILE = ProfessionalProfile()


# Funções auxiliares para consulta do perfil profissional (normalizadas em minúsculas)

def get_all_skills() -> tuple[str, ...]:
    """Retorna uma tupla contendo todas as competências (principais e complementares)."""
    return tuple(sorted(set(PROFILE.core_skills + PROFILE.complementary_skills)))


def get_all_keywords() -> tuple[str, ...]:
    """Retorna uma tupla contendo todas as palavras-chave (prioritárias e secundárias)."""
    return tuple(sorted(set(PROFILE.priority_keywords + PROFILE.secondary_keywords)))


def get_primary_keywords() -> tuple[str, ...]:
    """Retorna as palavras-chave principais."""
    return PROFILE.priority_keywords


def get_secondary_keywords() -> tuple[str, ...]:
    """Retorna as palavras-chave secundárias."""
    return PROFILE.secondary_keywords


def get_target_roles() -> tuple[str, ...]:
    """Retorna os cargos-alvo principais."""
    return PROFILE.target_roles


def get_high_priority_roles() -> tuple[str, ...]:
    """Retorna os cargos normalizados de alta prioridade."""
    return PROFILE.high_priority_roles


def get_secondary_roles() -> tuple[str, ...]:
    """Retorna os cargos normalizados de prioridade secundária."""
    return PROFILE.secondary_roles_keywords


def get_opportunity_roles() -> tuple[str, ...]:
    """Retorna os cargos normalizados de oportunidade."""
    return PROFILE.opportunity_roles_keywords


def get_preferred_levels() -> tuple[str, ...]:
    """Retorna os níveis de senioridade preferenciais."""
    return PROFILE.preferred_levels


def get_acceptable_levels() -> tuple[str, ...]:
    """Retorna os níveis de senioridade aceitáveis."""
    return PROFILE.acceptable_levels


def get_avoid_levels() -> tuple[str, ...]:
    """Retorna os níveis de senioridade a serem penalizados/evitados."""
    return PROFILE.avoid_levels


def get_core_skills() -> tuple[str, ...]:
    """Retorna as competências principais."""
    return PROFILE.core_skills


def get_complementary_skills() -> tuple[str, ...]:
    """Retorna as competências complementares."""
    return PROFILE.complementary_skills


def get_profile_summary() -> dict[str, any]:
    """Retorna um dicionário resumo com as principais informações do perfil."""
    return {
        "name": PROFILE.name,
        "location": PROFILE.location,
        "total_target_roles": len(PROFILE.target_roles),
        "total_secondary_roles": len(PROFILE.secondary_roles),
        "total_opportunity_roles": len(PROFILE.opportunity_roles),
        "total_core_skills": len(PROFILE.core_skills),
        "total_complementary_skills": len(PROFILE.complementary_skills),
        "experience_count": len(PROFILE.experience),
        "education_count": len(PROFILE.education),
    }


if __name__ == "__main__":
    print("=" * 60)
    print("MAV — PERFIL PROFISSIONAL")
    print("=" * 60)
    print(f"\nNome: {PROFILE.name}")
    print(f"Localização: {PROFILE.location}")
    print(f"Área de Atuação Principal: {', '.join(PROFILE.primary_areas)}")
    
    print("\nCARGOS — PRIORIDADE ALTA")
    for role in PROFILE.target_roles[:6]:
        print(f"  - {role}")
    print("  (...)")

    print("\nCARGOS — PRIORIDADE SECUNDÁRIA")
    for role in PROFILE.secondary_roles[:5]:
        print(f"  - {role}")
    print("  (...)")

    print("\nCARGOS — OPORTUNIDADES")
    for role in PROFILE.opportunity_roles[:5]:
        print(f"  - {role}")
    print("  (...)")

    print("\nÁREAS PRINCIPAIS")
    for area in PROFILE.primary_areas:
        print(f"  - {area}")

    print("\nÁREAS SECUNDÁRIAS")
    for area in PROFILE.secondary_areas:
        print(f"  - {area}")

    print("\nCOMPETÊNCIAS PRINCIPAIS")
    print(f"  Total cadastradas: {len(PROFILE.core_skills)}")
    print(f"  Exemplos: {', '.join(PROFILE.core_skills[:8])}...")

    print("\nCOMPETÊNCIAS COMPLEMENTARES")
    print(f"  Total cadastradas: {len(PROFILE.complementary_skills)}")
    print(f"  Exemplos: {', '.join(PROFILE.complementary_skills[:8])}...")

    print("\nSENIORIDADE")
    print(f"  Preferenciais: {', '.join(PROFILE.preferred_levels)}")
    print(f"  Aceitáveis: {', '.join(PROFILE.acceptable_levels)}")
    print(f"  A evitar / Penalizar: {', '.join(PROFILE.avoid_levels)}")

    print("\nRESUMO")
    summary = get_profile_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("Perfil carregado com sucesso.")
    print("=" * 60)
