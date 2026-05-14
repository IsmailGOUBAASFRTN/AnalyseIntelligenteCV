import os
import re
import logging
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("La variable d'environnement GEMINI_API_KEY n'est pas définie.")
genai.configure(api_key=API_KEY)

_MAX_INPUT_CHARS = 50_000  # ~12 500 tokens
_DANGEROUS_PATTERNS = re.compile(
    r"(ignore (all|previous|above) instructions?|"
    r"disregard (all|your) (previous )?instructions?|"
    r"you are now|forget (everything|all)|"
    r"new instructions?:|system prompt)",
    re.IGNORECASE,
)


def _sanitize(text: str, max_chars: int = _MAX_INPUT_CHARS) -> str:
    """Tronque et nettoie le texte pour prévenir l'injection de prompt."""
    text = text[:max_chars]
    # Retrait de patterns d'injection courants
    text = _DANGEROUS_PATTERNS.sub("[CONTENU SUPPRIMÉ]", text)
    return text


def get_analysis(job_description: str, cv_text: str) -> str:
    job_description = _sanitize(job_description, 10_000)
    cv_text = _sanitize(cv_text, 40_000)

    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = f"""
Tu es un expert senior en recrutement, chasseur de têtes et coach carrière avec 20 ans d'expérience.
Tu travailles pour un cabinet de recrutement de premier plan et tu dois remettre une analyse de haute qualité à ton client recruteur.

═══════════════════════════════════════════
RÈGLES ABSOLUES — À RESPECTER IMPÉRATIVEMENT
═══════════════════════════════════════════
1. Réponds UNIQUEMENT avec un objet JSON valide et complet.
2. AUCUN texte avant ou après le JSON. Pas de ```json, pas de commentaires.
3. Chaque champ listé ci-dessous est OBLIGATOIRE — ne laisse aucun champ vide ou null.
4. Tous les textes sont en FRANÇAIS.
5. Sois factuel : chaque évaluation doit être justifiée par un élément concret du CV ou du poste.

═══════════════════════════════════════════
STRUCTURE JSON REQUISE
═══════════════════════════════════════════

{{
  "score": <entier 0-100, adéquation globale CV/poste>,
  "score_justification": "<1 phrase expliquant ce score de façon factuelle>",

  "hiring_recommendation": "<exactement l'une des valeurs : 'Fortement recommandé' | 'Recommandé' | 'À considérer' | 'Non recommandé'>",
  "seniority_level": "<niveau détecté dans le CV : 'Junior (0-2 ans)' | 'Confirmé (3-5 ans)' | 'Senior (6-10 ans)' | 'Expert (10+ ans)'>",
  "years_of_experience": <entier estimé du nombre d'années d'expérience totales du candidat>,

  "summary": "<analyse synthétique de 4-5 phrases couvrant : profil global du candidat, adéquation au poste, points forts majeurs, lacunes principales, verdict global>",

  "matching_keywords": ["<compétence/technologie/diplôme du poste PRÉSENT dans le CV>"],
  "missing_keywords": ["<compétence/technologie/diplôme du poste ABSENT du CV>"],

  "strengths": [
    "<point fort précis et argumenté avec référence à un élément concret du CV>"
  ],

  "improvements": [
    "<action concrète et actionnable que le candidat devrait faire pour ce poste (ex: 'Obtenir une certification X', 'Mettre en avant Y')>"
  ],

  "red_flags": [
    "<élément préoccupant du CV : trou d'emploi, instabilité, compétence manquante critique, ou 'Aucun' si rien à signaler>"
  ],

  "technical_gaps": [
    "<compétence technique spécifiquement requise par le poste et absente ou insuffisante dans le CV>"
  ],

  "cover_letter_tips": [
    "<conseil précis pour rédiger une lettre de motivation percutante pour CE poste spécifique>"
  ],

  "skills_rating": {{
    "Compétences Techniques": <0-10>,
    "Expérience Professionnelle": <0-10>,
    "Formation": <0-10>,
    "Langues": <0-10>,
    "Compétences Interpersonnelles": <0-10>
  }},

  "experience_gap": "<écart entre l'expérience requise et celle du candidat, ex: 'Le poste exige 5 ans, le candidat en a 3' ou 'Aucun écart'>",

  "alternative_jobs": [
    "<intitulé de poste alternatif pour lequel ce profil serait encore plus adapté>"
  ],

  "interview_questions": [
    {{
      "question": "<question d'entretien pertinente et ciblée sur CE candidat>",
      "objectif": "<ce que cette question cherche à évaluer : compétence, lacune, comportement>",
      "reponse_attendue": "<réponse idéale détaillée que le recruteur devrait attendre d'un bon candidat, avec les éléments clés à mentionner>",
      "conseil_recruteur": "<signe positif ou négatif à observer dans la réponse du candidat>"
    }}
  ]
}}

IMPORTANT : Le tableau "interview_questions" doit contenir EXACTEMENT 10 questions minimum, réparties ainsi :
- 3 questions techniques (compétences du poste)
- 2 questions comportementales (méthode STAR : Situation, Tâche, Action, Résultat)
- 2 questions sur les lacunes détectées dans le CV
- 2 questions de mise en situation (cas pratique lié au poste)
- 1 question de motivation/projet professionnel

═══════════════════════════════════════════
FICHE DE POSTE
═══════════════════════════════════════════
{job_description}

═══════════════════════════════════════════
CV DU CANDIDAT
═══════════════════════════════════════════
{cv_text}

═══════════════════════════════════════════
ANALYSE JSON (commence directement par {{)
═══════════════════════════════════════════
"""

    try:
        response = model.generate_content(
            prompt,
            request_options={"timeout": 60},
        )
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '').strip()
        return cleaned_response
    except Exception as e:
        logger.error("Erreur API Gemini : %s", e)
        raise RuntimeError(f"Impossible d'obtenir l'analyse depuis l'API Gemini : {e}") from e
