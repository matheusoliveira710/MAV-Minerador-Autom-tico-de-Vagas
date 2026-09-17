from dataclasses import dataclass, field
import hashlib
import re

@dataclass
class Job:

    title: str

    company: str

    location: str

    link: str

    source: str

    description_snippet: str = ""

    matched_categories: list[str] = field(
        default_factory=list
    )

    score: int = 0

    # ========================================================
    # ID ÚNICO
    # ========================================================

    def unique_id(self) -> str:
                """
                Gera um identificador estável para a vaga.

                No APInfo, o parâmetro codvaga identifica a vaga.
                O parâmetro pkey é dinâmico e não deve participar
                da deduplicação.
                """

                if self.source.strip().lower() == "apinfo":
                    match = re.search(
                        r"[?&]codvaga=(\d+)",
                        self.link,
                        re.IGNORECASE,
                    )

                    if match:
                        stable_id = (
                            f"APInfo:{match.group(1)}"
                        )

                        return hashlib.sha256(
                            stable_id.encode("utf-8")
                        ).hexdigest()

                return hashlib.sha256(
                self.link.encode("utf-8")
            ).hexdigest()

    # ========================================================
    # FILTRO
    # ========================================================

    def normalize(self) -> 'Job':
        """
        Realiza uma normalização conservadora dos dados da vaga:
        - Remove espaços extras nas pontas (strip)
        - Converte None ou campos ausentes em strings vazias seguras
        - Preserva rigorosamente a acentuação e caracteres UTF-8 originais
        """
        return Job(
            title=str(self.title).strip() if self.title else "",
            company=str(self.company).strip() if self.company else "",
            location=str(self.location).strip() if self.location else "",
            link=str(self.link).strip() if self.link else "",
            source=str(self.source).strip() if self.source else "",
            description_snippet=str(self.description_snippet).strip() if self.description_snippet else ""
        )

    def matches_keywords(
        self,
        keywords: dict[str, list[str]],
        exclude_keywords: list[str],
        category_weights: dict[str, int],
        minimum_score: int = 5,
    ) -> bool:

        text = (
            f"{self.title} "
            f"{self.description_snippet}"
        ).lower()

        # ----------------------------------------------------
        # EXCLUSÕES
        # ----------------------------------------------------

        for keyword in exclude_keywords:

            if keyword.lower() in text:

                self.score = 0
                self.matched_categories.clear()

                return False

        # ----------------------------------------------------
        # RESET
        # ----------------------------------------------------

        self.matched_categories.clear()

        self.score = 0

        # ----------------------------------------------------
        # CATEGORIAS
        # ----------------------------------------------------

        for category, terms in keywords.items():

            category_found = False

            for term in terms:

                if term.lower() in text:

                    category_found = True

                    break

            if category_found:

                self.matched_categories.append(
                    category
                )

                self.score += (
                    category_weights.get(
                        category,
                        1
                    )
                )

        # ----------------------------------------------------
        # RESULTADO
        # ----------------------------------------------------

        return self.score >= minimum_score
