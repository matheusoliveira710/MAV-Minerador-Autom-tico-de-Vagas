"""
MAV — Minerador Automático de Vagas
Definição do modelo de dados (Job) e métodos auxiliares de normalização conservadora.
"""

import hashlib
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Job:
    title: str
    company: str
    location: str
    link: str
    source: str
    description_snippet: str = ""

    def unique_id(self) -> str:
        """Gera um hash estável (sha256 do link ou título/empresa) para deduplicação."""
        clean_link = self.link.strip() if self.link else f"{self.title}-{self.company}"
        return hashlib.sha256(clean_link.encode('utf-8')).hexdigest()

    def matches_keywords(self, keywords: list[str], exclude_keywords: list[str]) -> bool:
        """Checa título + descrição contra keywords (case-insensitive) e lista de exclusão."""
        text_to_check = f"{self.title} {self.description_snippet}".lower()

        for exc in exclude_keywords:
            if exc.lower() in text_to_check:
                return False

        for kw in keywords:
            if kw.lower() in text_to_check:
                return True

        return False

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
