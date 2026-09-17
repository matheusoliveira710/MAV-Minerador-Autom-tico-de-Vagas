"""
MAV — ETAPA 2: TESTE DE VARIAÇÕES DE COMPETÊNCIAS

Objetivo:
Validar se o matcher reconhece corretamente diferentes formas
de escrita das competências técnicas presentes no profile.py.

Execução:
    python -m tests.test_skill_variations
"""

from matcher import match_job


# ================================================================
# DADOS DE TESTE
# ================================================================

TEST_CASES = [
    # ------------------------------------------------------------
    # SUPORTE
    # ------------------------------------------------------------

    ("Suporte técnico", "suporte técnico"),
    ("Suporte de TI", "suporte de ti"),
    ("Help Desk", "help desk"),
    ("Helpdesk", "helpdesk"),
    ("Service Desk", "service desk"),
    ("Suporte N1", "suporte n1"),
    ("Suporte N2", "suporte n2"),
    ("Troubleshooting", "troubleshooting"),
    ("Gestão de chamados", "gestão de chamados"),

    # ------------------------------------------------------------
    # SISTEMAS OPERACIONAIS
    # ------------------------------------------------------------

    ("Windows", "windows"),
    ("Windows 10", "windows 10"),
    ("Windows 11", "windows 11"),
    ("Linux", "linux"),
    ("Ubuntu", "ubuntu"),
    ("Ubuntu Server", "ubuntu server"),

    # ------------------------------------------------------------
    # REDES
    # ------------------------------------------------------------

    ("Redes", "redes"),
    ("Rede", "rede"),
    ("TCP/IP", "tcp/ip"),
    ("TCP", "tcp"),
    ("IP", "ip"),
    ("Infraestrutura de Redes", "infraestrutura de redes"),
    ("Rede Local", "rede local"),
    ("LAN", "lan"),

    # ------------------------------------------------------------
    # IDENTIDADE
    # ------------------------------------------------------------

    ("Active Directory", "active directory"),
    ("AD", "ad"),
    ("Administração de usuários", "administração de usuários"),
    ("Contas de usuário", "contas de usuário"),

    # ------------------------------------------------------------
    # HARDWARE
    # ------------------------------------------------------------

    ("Hardware", "hardware"),
    ("Manutenção de hardware", "manutenção de hardware"),
    ("Computadores", "computadores"),
    ("Notebooks", "notebooks"),
    ("Periféricos", "periféricos"),
    ("Manutenção de computadores", "manutenção de computadores"),

    # ------------------------------------------------------------
    # MICROSOFT
    # ------------------------------------------------------------

    ("Microsoft 365", "microsoft 365"),
    ("Office 365", "office 365"),
    ("Microsoft", "microsoft"),

    # ------------------------------------------------------------
    # ACESSO REMOTO
    # ------------------------------------------------------------

    ("TeamViewer", "teamviewer"),
    ("Acesso remoto", "acesso remoto"),
    ("Suporte remoto", "suporte remoto"),

    # ------------------------------------------------------------
    # VIRTUALIZAÇÃO
    # ------------------------------------------------------------

    ("VirtualBox", "virtualbox"),
    ("Virtualização", "virtualização"),
    ("Virtualizacao", "virtualizacao"),
    ("Máquinas virtuais", "máquinas virtuais"),
    ("VM", "vm"),
    ("VMs", "vms"),

    # ------------------------------------------------------------
    # SERVIDORES
    # ------------------------------------------------------------

    ("Servidor", "servidor"),
    ("Servidores", "servidores"),
    ("Administração de servidores", "administração de servidores"),
    ("Linux Server", "linux server"),
    ("Backup", "backup"),

    # ------------------------------------------------------------
    # DESENVOLVIMENTO
    # ------------------------------------------------------------

    ("Python", "python"),
    ("JavaScript", "javascript"),
    ("HTML", "html"),
    ("HTML5", "html5"),
    ("CSS", "css"),
    ("CSS3", "css3"),
    ("React", "react"),
    ("SQL", "sql"),
    ("MySQL", "mysql"),

    # ------------------------------------------------------------
    # AUTOMAÇÃO
    # ------------------------------------------------------------

    ("Automação", "automação"),
    ("Automacao", "automacao"),
    ("Scripts", "scripts"),
    ("Ansible", "ansible"),
    ("Playbooks", "playbooks"),

    # ------------------------------------------------------------
    # VERSIONAMENTO
    # ------------------------------------------------------------

    ("Git", "git"),
    ("GitHub", "github"),
    ("Controle de versão", "controle de versão"),
    ("Controle de versao", "controle de versao"),

    # ------------------------------------------------------------
    # SEGURANÇA
    # ------------------------------------------------------------

    ("Segurança da Informação", "segurança da informação"),
    ("Seguranca da Informacao", "seguranca da informacao"),
    ("Segurança", "segurança"),
    ("Seguranca", "seguranca"),

    # ------------------------------------------------------------
    # CLOUD
    # ------------------------------------------------------------

    ("Computação em nuvem", "computação em nuvem"),
    ("Computacao em nuvem", "computacao em nuvem"),
    ("Cloud Computing", "cloud computing"),
    ("Cloud", "cloud"),
]


# ================================================================
# EXECUÇÃO DOS TESTES
# ================================================================

def main() -> None:
    print("=" * 70)
    print("MAV — ETAPA 2: TESTE DE VARIAÇÕES DE COMPETÊNCIAS")
    print("=" * 70)

    passed = 0
    failed = 0

    for index, (skill_name, skill_text) in enumerate(TEST_CASES, start=1):

        job = {
            "title": "Analista de Suporte",
            "description": (
                f"Vaga para profissional de TI com experiência em "
                f"{skill_text}."
            ),
            "location": "Campinas - SP",
        }

        result = match_job(job)

        matched_text = " ".join(
            str(value).lower()
            for value in result.values()
        )

        normalized_skill = skill_text.lower()

        detected = (
            normalized_skill in matched_text
            or any(
                normalized_skill in str(skill).lower()
                for skill in result.get("matched_core_skills", [])
            )
            or any(
                normalized_skill in str(skill).lower()
                for skill in result.get("matched_complementary_skills", [])
            )
            or any(
                normalized_skill in str(keyword).lower()
                for keyword in result.get("matched_keywords", [])
            )
        )

        if detected:
            passed += 1
            status = "✅ PASSOU"
        else:
            failed += 1
            status = "❌ FALHOU"

        print()
        print(f"[{index:02d}] {skill_name}")
        print(f"     Score: {result.get('score', 0)}")
        print(f"     Core Skills: {result.get('matched_core_skills', [])}")
        print(
            f"     Complementares: "
            f"{result.get('matched_complementary_skills', [])}"
        )
        print(f"     Keywords: {result.get('matched_keywords', [])}")
        print(f"     {status}")

    # ============================================================
    # RESULTADO
    # ============================================================

    total = len(TEST_CASES)

    print()
    print("=" * 70)
    print("RESULTADO — ETAPA 2")
    print("=" * 70)
    print(f"Testes executados: {total}")
    print(f"Passaram:          {passed}")
    print(f"Falharam:          {failed}")

    if failed == 0:
        print()
        print("✅ TODOS OS TESTES DE COMPETÊNCIAS PASSARAM!")
    else:
        print()
        print("⚠️ Existem competências que o matcher não reconheceu.")

    print("=" * 70)

    assert failed == 0, (
        f"{failed} teste(s) de competência falharam."
    )


if __name__ == "__main__":
    main()
