"""
MAV — Minerador Automático de Vagas
Módulo de Matcher e Pontuação de Compatibilidade Profissional.
Compatível com Python 3.12 e Windows 11.
"""

from dataclasses import dataclass, field
import unicodedata
import re
from typing import Any, Dict, List, Tuple, Optional

from profile import PROFILE


def normalize_text(text: Optional[str]) -> str:
    """
    Normaliza o texto para comparação robusta:
    - Converte para minúsculas
    - Remove acentos e diacríticos (ex: 'júnior' -> 'junior')
    - Substitui hífens por espaços para tratar variações compostas
    - Padroniza múltiplos espaços em branco
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove acentos
    nfkd = unicodedata.normalize('NFKD', text)
    without_accents = "".join([c for c in nfkd if not unicodedata.combining(c)])
    
    # Converte para minúsculas
    lower_text = without_accents.lower()
    
    # Trata hífens como espaços (ex: "home-office" -> "home office", "back-end" -> "back end")
    cleaned_hyphens = lower_text.replace("-", " ")
    
    # Remove pontuações extras mantendo caracteres alfanuméricos e espaços
    alphanumeric = re.sub(r'[^a-z0-9\s]', ' ', cleaned_hyphens)
    
    # Normaliza espaços múltiplos
    normalized_spaces = re.sub(r'\s+', ' ', alphanumeric).strip()
    
    return normalized_spaces


@dataclass
class MatchResult:
    score: float
    classification: str
    matched_roles: List[str] = field(default_factory=list)
    matched_core_skills: List[str] = field(default_factory=list)
    matched_complementary_skills: List[str] = field(default_factory=list)
    matched_keywords: List[str] = field(default_factory=list)
    matched_categories: List[str] = field(default_factory=list)
    seniority_match: str = "Não identificada"
    location_match: str = "Não informada"
    work_mode_match: str = "Não informada"
    penalties: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": round(self.score, 2),
            "classification": self.classification,
            "matched_roles": self.matched_roles,
            "matched_core_skills": self.matched_core_skills,
            "matched_complementary_skills": self.matched_complementary_skills,
            "matched_keywords": self.matched_keywords,
            "matched_categories": self.matched_categories,
            "seniority_match": self.seniority_match,
            "location_match": self.location_match,
            "work_mode_match": self.work_mode_match,
            "penalties": self.penalties,
            "reasons": self.reasons,
        }


class JobMatcher:
    """
    Realiza o cruzamento de dados entre uma vaga de emprego (compatível com a dataclass Job do models.py)
    e o ProfessionalProfile, calculando uma pontuação normalizada de 0 a 100 com explicações detalhadas.
    """

    def __init__(self, profile: Any = PROFILE):
        self.profile = profile
        
        # Pré-normalização de termos do perfil para otimização de busca
        self.norm_high_roles = [normalize_text(r) for r in (getattr(self.profile, "high_priority_roles", None) or self.profile.target_roles)]
        self.norm_secondary_roles = [normalize_text(r) for r in (getattr(self.profile, "secondary_roles_keywords", None) or self.profile.secondary_roles)]
        self.norm_opportunity_roles = [normalize_text(r) for r in (getattr(self.profile, "opportunity_roles_keywords", None) or self.profile.opportunity_roles)]
        
        # Constrói o conjunto base de core skills e injeta explicitamente variações essenciais se necessário
        base_core = set(list(self.profile.core_skills))
        for extra_s in ["microsoft", "tcp", "ip", "manutenção de computadores"]:
            if extra_s not in base_core:
                base_core.add(extra_s)

        # Ordena as skills por tamanho decrescente (frases compostas mais longas primeiro, ex: "manutenção de computadores")
        sorted_core = sorted(list(base_core), key=lambda x: len(x.split()), reverse=True)
        self.norm_core_skills = [(orig, normalize_text(orig)) for orig in sorted_core]

        sorted_comp = sorted(list(self.profile.complementary_skills), key=lambda x: len(x.split()), reverse=True)
        self.norm_complementary_skills = [(orig, normalize_text(orig)) for orig in sorted_comp]
        
        self.norm_priority_kw = [normalize_text(k) for k in self.profile.priority_keywords]
        self.norm_secondary_kw = [normalize_text(k) for k in self.profile.secondary_keywords]
        
        self.norm_low_relevance = [normalize_text(k) for k in self.profile.low_relevance_keywords]
        
        self.norm_preferred_locations = [normalize_text(l) for l in self.profile.preferred_locations]
        self.norm_regional_locations = [normalize_text(l) for l in self.profile.regional_locations]
        
        self.norm_work_modes = [normalize_text(m) for m in self.profile.preferred_work_modes]
        
        self.norm_preferred_levels = [normalize_text(l) for l in self.profile.preferred_levels]
        self.norm_acceptable_levels = [normalize_text(l) for l in self.profile.acceptable_levels]
        self.norm_avoid_levels = [normalize_text(l) for l in self.profile.avoid_levels]
        
        # Pré-processamento das categorias técnicas normalizadas
        self.norm_technical_categories: Dict[str, List[str]] = {}
        if hasattr(self.profile, "technical_skills") and self.profile.technical_skills:
            for cat, skills in self.profile.technical_skills.items():
                self.norm_technical_categories[cat] = [normalize_text(s) for s in skills]

    def _job_to_text(self, job: Any) -> Tuple[str, str, str, str]:
        """
        Extrai e consolida os campos reais da struct/dataclass Job do projeto (models.py):
        - title (ou cargo)
        - company (ou empresa)
        - location (ou local)
        - description_snippet (ou description, texto)
        Retorna (norm_title, norm_location, norm_company, full_text).
        """
        title = str(
            getattr(job, "title", None) or 
            getattr(job, "cargo", None) or 
            (job.get("title") if isinstance(job, dict) else None) or 
            (job.get("cargo") if isinstance(job, dict) else None) or ""
        )
        description = str(
            getattr(job, "description_snippet", None) or 
            getattr(job, "description", None) or 
            getattr(job, "texto", None) or 
            (job.get("description_snippet") if isinstance(job, dict) else None) or 
            (job.get("description") if isinstance(job, dict) else None) or 
            (job.get("texto") if isinstance(job, dict) else None) or ""
        )
        company = str(
            getattr(job, "company", None) or 
            getattr(job, "empresa", None) or 
            (job.get("company") if isinstance(job, dict) else None) or 
            (job.get("empresa") if isinstance(job, dict) else None) or ""
        )
        location = str(
            getattr(job, "location", None) or 
            getattr(job, "local", None) or 
            (job.get("location") if isinstance(job, dict) else None) or 
            (job.get("local") if isinstance(job, dict) else None) or ""
        )
        
        norm_title = normalize_text(title)
        norm_location = normalize_text(location)
        norm_company = normalize_text(company)
        full_text = normalize_text(f"{title} {description} {company} {location}")
        
        return norm_title, norm_location, norm_company, full_text

    def match(self, job: Any) -> MatchResult:
        """
        Analisa o objeto Job e retorna um MatchResult detalhado com pontuação de 0 a 100.
        """
        norm_title, norm_location, norm_company, full_text = self._job_to_text(job)
        
        raw_location = str(
            getattr(job, "location", None) or 
            getattr(job, "local", None) or 
            (job.get("location") if isinstance(job, dict) else None) or 
            (job.get("local") if isinstance(job, dict) else None) or ""
        )

        matched_roles = []
        matched_core_skills = []
        matched_complementary_skills = []
        matched_keywords = []
        matched_categories = []
        penalties = []
        reasons = []

        # -------------------------------------------------------------
        # 1. ANÁLISE DE CARGOS (Até 30 pontos) — Mantido intacto da Etapa 1
        # -------------------------------------------------------------
        role_score = 0.0
        role_found = False

        high_roles_orig = getattr(self.profile, "high_priority_roles", None) or self.profile.target_roles
        for orig_role, norm_role in zip(high_roles_orig, self.norm_high_roles):
            if norm_role and norm_role in norm_title:
                role_score = 30.0
                if orig_role not in matched_roles:
                    matched_roles.append(orig_role)
                reasons.append(f"Cargo de alta prioridade exato no título: '{orig_role}' (+30 pts)")
                role_found = True
                break
            elif norm_role and norm_role in full_text:
                role_score = max(role_score, 20.0)
                if orig_role not in matched_roles:
                    matched_roles.append(orig_role)
                reasons.append(f"Cargo de alta prioridade encontrado no texto: '{orig_role}' (+20 pts)")
                role_found = True

        if role_score < 30.0:
            sec_roles_orig = getattr(self.profile, "secondary_roles_keywords", None) or self.profile.secondary_roles
            for orig_role, norm_role in zip(sec_roles_orig, self.norm_secondary_roles):
                if norm_role and norm_role in norm_title:
                    role_score = max(role_score, 22.0)
                    if orig_role not in matched_roles:
                        matched_roles.append(orig_role)
                    reasons.append(f"Cargo de prioridade secundária no título: '{orig_role}' (+22 pts)")
                    role_found = True
                    break
                elif norm_role and norm_role in full_text:
                    role_score = max(role_score, 15.0)
                    if orig_role not in matched_roles:
                        matched_roles.append(orig_role)
                    reasons.append(f"Cargo de prioridade secundária encontrado: '{orig_role}' (+15 pts)")
                    role_found = True

        if role_score < 15.0:
            opp_roles_orig = getattr(self.profile, "opportunity_roles_keywords", None) or self.profile.opportunity_roles
            for orig_role, norm_role in zip(opp_roles_orig, self.norm_opportunity_roles):
                if norm_role and norm_role in norm_title:
                    role_score = max(role_score, 18.0)
                    if orig_role not in matched_roles:
                        matched_roles.append(orig_role)
                    reasons.append(f"Cargo de oportunidade no título: '{orig_role}' (+18 pts)")
                    role_found = True
                    break
                elif norm_role and norm_role in full_text:
                    role_score = max(role_score, 10.0)
                    if orig_role not in matched_roles:
                        matched_roles.append(orig_role)
                    reasons.append(f"Cargo de oportunidade encontrado: '{orig_role}' (+10 pts)")
                    role_found = True

        if not role_found:
            reasons.append("Nenhum cargo-alvo direto identificado no título ou descrição.")

        # -------------------------------------------------------------
        # 2. CORE SKILLS (Até 30 pontos) — Com Matching Robusto (Word Boundary e Longest Match)
        # -------------------------------------------------------------
        core_score = 0.0
        core_matches_count = 0
        consumed_spans = []

        for orig_skill, norm_skill in self.norm_core_skills:
            if not norm_skill:
                continue
            
            # Tratamento seguro para termos curtos ou siglas isoladas (ex: "ip", "tcp", "ad")
            if len(norm_skill) <= 3:
                pattern = r'\b' + re.escape(norm_skill) + r'\b'
            else:
                pattern = r'\b' + re.escape(norm_skill) + r'(?:s|es)?\b'

            for match in re.finditer(pattern, full_text):
                span = match.span()
                overlap = any(max(span[0], s[0]) < min(span[1], s[1]) for s in consumed_spans)
                if not overlap:
                    consumed_spans.append(span)
                    if orig_skill not in matched_core_skills:
                        matched_core_skills.append(orig_skill)
                    core_matches_count += 1
                    break

        if core_matches_count > 0:
            core_score = min(30.0, float(core_matches_count * 5.0))
            reasons.append(f"Identificadas {core_matches_count} competência(s) principal(is) (Core Skills) (+{core_score:.1f} pts)")
        else:
            reasons.append("Nenhuma Core Skill identificada na vaga.")

        # -------------------------------------------------------------
        # 3. COMPLEMENTARY SKILLS (Até 10 pontos)
        # -------------------------------------------------------------
        comp_score = 0.0
        comp_matches_count = 0
        for orig_skill, norm_skill in self.norm_complementary_skills:
            if not norm_skill:
                continue
            if len(norm_skill) <= 3:
                pattern = r'\b' + re.escape(norm_skill) + r'\b'
            else:
                pattern = r'\b' + re.escape(norm_skill) + r'(?:s|es)?\b'

            if re.search(pattern, full_text):
                if orig_skill not in matched_complementary_skills:
                    matched_complementary_skills.append(orig_skill)
                comp_matches_count += 1

        if comp_matches_count > 0:
            comp_score = min(10.0, float(comp_matches_count * 2.5))
            reasons.append(f"Identificadas {comp_matches_count} competência(s) complementar(es) (+{comp_score:.1f} pts)")

        # -------------------------------------------------------------
        # 4. KEYWORDS (Até 10 pontos)
        # -------------------------------------------------------------
        kw_score = 0.0
        p_kw_count = 0
        for orig_kw, norm_kw in zip(self.profile.priority_keywords, self.norm_priority_kw):
            if norm_kw and re.search(r'\b' + re.escape(norm_kw) + r'\b', full_text):
                if orig_kw not in matched_keywords:
                    matched_keywords.append(orig_kw)
                p_kw_count += 1

        s_kw_count = 0
        for orig_kw, norm_kw in zip(self.profile.secondary_keywords, self.norm_secondary_kw):
            if norm_kw and re.search(r'\b' + re.escape(norm_kw) + r'\b', full_text):
                if orig_kw not in matched_keywords:
                    matched_keywords.append(orig_kw)
                s_kw_count += 1

        kw_score = min(10.0, float((p_kw_count * 2.0) + (s_kw_count * 1.0)))
        if p_kw_count > 0 or s_kw_count > 0:
            reasons.append(f"Palavras-chave encontradas: {p_kw_count} prioritárias, {s_kw_count} secundárias (+{kw_score:.1f} pts)")

        # -------------------------------------------------------------
        # 5. CATEGORIAS TÉCNICAS
        # -------------------------------------------------------------
        matched_categories_count = 0
        for cat, skills in self.norm_technical_categories.items():
            cat_matched = False
            for s in skills:
                if s and re.search(r'\b' + re.escape(s) + r'\b', full_text):
                    cat_matched = True
                    break
            if cat_matched:
                matched_categories.append(cat)
                matched_categories_count += 1

        if matched_categories_count > 0:
            reasons.append(f"Cobertura de {matched_categories_count} categoria(s) técnica(s) ({', '.join(matched_categories[:3])})")

        # -------------------------------------------------------------
        # 6. SENIORIDADE (Até 10 pontos + Penalizações)
        # -------------------------------------------------------------
        seniority_score = 5.0
        seniority_match = "Não especificada"
        
        is_preferred = any(re.search(r'\b' + re.escape(lvl) + r'\b', full_text) for lvl in self.norm_preferred_levels)
        is_acceptable = any(re.search(r'\b' + re.escape(lvl) + r'\b', full_text) for lvl in self.norm_acceptable_levels)
        is_avoid = any(re.search(r'\b' + re.escape(lvl) + r'\b', full_text) for lvl in self.norm_avoid_levels)

        if is_avoid:
            seniority_score = -5.0
            seniority_match = "Sênior / Gestão / Especialista (Evitar/Penalizar)"
            penalties.append("Senioridade acima do perfil júnior/estágio (-15 pts aplicados)")
            reasons.append("Detectada senioridade sênior ou de liderança/especialista na vaga.")
        elif is_preferred:
            seniority_score = 10.0
            seniority_match = "Estágio / Júnior (Preferencial)"
            reasons.append("Senioridade compatível com estágio ou júnior (+10 pts)")
        elif is_acceptable:
            seniority_score = 7.0
            seniority_match = "Pleno (Aceitável)"
            reasons.append("Senioridade pleno considerada aceitável (+7 pts)")
        else:
            seniority_match = "Não especificada explicitamente (Neutro)"

        # -------------------------------------------------------------
        # 7. LOCALIZAÇÃO (Até 5 pontos)
        # -------------------------------------------------------------
        location_score = 2.5
        location_match = "Não informada"

        if any(loc in norm_location for loc in self.norm_preferred_locations):
            location_score = 5.0
            location_match = "Campinas - SP (Preferencial)"
            reasons.append("Localização exata em Campinas (+5 pts)")
        elif any(loc in norm_location for loc in self.norm_regional_locations):
            location_score = 4.0
            location_match = "Região metropolitana de Campinas (Aceitável)"
            reasons.append("Localização em cidade da região de Campinas (+4 pts)")
        elif "remoto" in full_text or "home office" in full_text:
            location_score = 5.0
            location_match = "Remoto / Home Office"
            reasons.append("Vaga remota identificada (+5 pts)")
        elif raw_location:
            location_match = f"Outra localidade: {raw_location}"
            reasons.append(f"Localizada fora da região principal ({raw_location}).")

        # -------------------------------------------------------------
        # 8. MODALIDADE (Até 5 pontos)
        # -------------------------------------------------------------
        work_mode_score = 3.0
        work_mode_match = "Não especificada"

        if "remoto" in full_text or "home office" in full_text or "home-office" in full_text:
            work_mode_score = 5.0
            work_mode_match = "Remoto / Home Office"
        elif "hibrido" in full_text or "híbrido" in full_text:
            work_mode_score = 4.0
            work_mode_match = "Híbrido"
        elif "presencial" in full_text:
            work_mode_score = 3.0
            work_mode_match = "Presencial"

        # -------------------------------------------------------------
        # 9. PENALIZAÇÃO POR TERMOS DE BAIXA RELEVÂNCIA
        # -------------------------------------------------------------
        low_relevance_found = 0
        for lr in self.norm_low_relevance:
            if lr and re.search(r'\b' + re.escape(lr) + r'\b', norm_title):
                low_relevance_found += 3
                penalties.append(f"Termo de baixa relevância no título: '{lr}'")
            elif lr and re.search(r'\b' + re.escape(lr) + r'\b', full_text):
                low_relevance_found += 1

        if low_relevance_found >= 2 and not any(r in norm_title for r in self.norm_high_roles + self.norm_secondary_roles + self.norm_opportunity_roles):
            role_score = 0.0
            penalties.append("Vaga fora da área de TI (Falso positivo evitado no cargo)")
            reasons.append("Termos comerciais/administrativos predominantes no título sem aderência aos cargos de TI.")

        # -------------------------------------------------------------
        # 10. CÁLCULO E NORMALIZAÇÃO DO SCORE FINAL (0 a 100)
        # -------------------------------------------------------------
        raw_score = (
            role_score +          # Max 30
            core_score +          # Max 30
            comp_score +          # Max 10
            kw_score +            # Max 10
            seniority_score +     # Max 10
            location_score +      # Max 5
            work_mode_score       # Max 5
        )

        penalty_reduction = 0.0
        if is_avoid:
            penalty_reduction += 15.0
        if low_relevance_found > 0:
            penalty_reduction += min(35.0, float(low_relevance_found * 10.0))
            penalties.append(f"Penalização por termos distantes do perfil (-{min(35.0, float(low_relevance_found * 10.0))} pts)")

        final_score = max(0.0, min(100.0, raw_score - penalty_reduction))
        classification = self._classify_score(final_score)

        return MatchResult(
            score=final_score,
            classification=classification,
            matched_roles=list(set(matched_roles)),
            matched_core_skills=list(set(matched_core_skills)),
            matched_complementary_skills=list(set(matched_complementary_skills)),
            matched_keywords=list(set(matched_keywords)),
            matched_categories=list(set(matched_categories)),
            seniority_match=seniority_match,
            location_match=location_match,
            work_mode_match=work_mode_match,
            penalties=penalties,
            reasons=reasons
        )

    def job_to_text_helper(self, job: Any) -> Tuple[str, str, str, str]:
        """Alias para _job_to_text exigido na especificação de testes."""
        return self._job_to_text(job)

    def _classify_score(self, score: float) -> str:
        if score >= 90.0:
            return "EXCELENTE"
        elif score >= 75.0:
            return "MUITO RELEVANTE"
        elif score >= 60.0:
            return "RELEVANTE"
        elif score >= 45.0:
            return "MODERADA"
        elif score >= 30.0:
            return "BAIXA"
        else:
            return "DESCARTAR"


def match_job(job: Any) -> Dict[str, Any]:
    """Função utilitária para compatibilidade com o ecossistema do MAV."""
    matcher = JobMatcher()
    result = matcher.match(job)
    return result.to_dict()


# Bloco de Teste Local Executável
if __name__ == "__main__":
    print("=" * 60)
    print("MAV — TESTE MANUAL DO MATCHER")
    print("=" * 60)
    matcher = JobMatcher()
    print("Matcher carregado e pronto para execução dos testes oficiais.")
    print("=" * 60)
