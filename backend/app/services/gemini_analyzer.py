import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

def get_analysis(job_description: str, cv_text: str) -> str:
    model = genai.GenerativeModel('gemini-2.5-pro')
    
    prompt = f"""
    Agis en tant qu'expert en recrutement. Analyse le CV fourni par rapport à la fiche de poste.
    Fournis une analyse structurée au format JSON STRICT. N'ajoute aucun texte avant ou après le JSON.

    Le JSON doit contenir les clés suivantes :
    - "score": un score global d'adéquation en pourcentage (nombre entier de 0 à 100).
    - "matching_keywords": une liste des mots-clés de la fiche de poste trouvés dans le CV.
    - "summary": un résumé de 2-3 phrases sur l'adéquation du candidat.
    - "strengths": une liste des points forts du CV par rapport au poste.
    - "improvements": une liste de suggestions concrètes pour améliorer le CV pour ce poste.
    - "alternative_jobs": une liste de 2 à 3 intitulés de postes alternatifs qui pourraient correspondre au profil.
    - "skills_rating": un objet JSON notant les compétences sur 10 dans les catégories suivantes : 'Compétences Techniques', 'Expérience Professionnelle', 'Formation', 'Langues', 'Compétences Interpersonnelles'.

    --- FICHE DE POSTE ---
    {job_description}

    --- CV ---
    {cv_text}

    --- ANALYSE JSON ---
    """

    try:
        response = model.generate_content(prompt)
        # Nettoyer la réponse pour ne garder que le JSON
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        return cleaned_response
    except Exception as e:
        return f'{{"error": "Failed to get analysis from Gemini API: {str(e)}"}}'
    