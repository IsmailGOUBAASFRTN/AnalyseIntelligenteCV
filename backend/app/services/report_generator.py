from fpdf import FPDF
from fastapi.responses import Response

def _safe(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    return text.encode('latin-1', 'replace').decode('latin-1')

class PDF(FPDF):
    def header(self):
        self.set_fill_color(30, 41, 59)
        self.rect(0, 0, 210, 22, 'F')
        self.set_font('Arial', 'B', 14)
        self.set_text_color(255, 255, 255)
        self.set_y(6)
        self.cell(0, 10, _safe('Rapport d\'Analyse de CV - Analyseur Intelligent'), 0, 1, 'C')
        self.set_text_color(0, 0, 0)
        self.ln(6)

    def footer(self):
        self.set_y(-12)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def section_title(self, title: str, r=30, g=41, b=59):
        self.set_x(self.l_margin)
        self.set_fill_color(r, g, b)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 11)
        self.cell(0, 8, _safe(f'  {title}'), 0, 1, 'L', fill=True)
        self.set_text_color(0, 0, 0)
        self.set_x(self.l_margin)
        self.ln(2)

    def body_text(self, text: str):
        self.set_x(self.l_margin)
        self.set_font('Arial', '', 10)
        self.multi_cell(self.w - self.l_margin - self.r_margin, 5, _safe(text))
        self.ln(1)

    def bullet_list(self, items: list):
        self.set_font('Arial', '', 10)
        w = self.w - self.l_margin - self.r_margin
        for item in items:
            self.set_x(self.l_margin)
            self.multi_cell(w, 5, _safe(f'  - {item}'))
        self.ln(2)

    def key_value(self, key: str, value: str):
        self.set_x(self.l_margin)
        self.set_font('Arial', 'B', 10)
        self.cell(65, 6, _safe(f'{key} :'), 0, 0)
        self.set_font('Arial', '', 10)
        self.cell(0, 6, _safe(str(value)[:120]), 0, 1)
        self.set_x(self.l_margin)


def generate_pdf_report(analysis_data) -> Response:
    data = analysis_data.analysis_data
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── En-tête identité ───────────────────────────────────────────
    pdf.set_font('Arial', 'B', 13)
    pdf.cell(0, 8, _safe(f'Poste : {analysis_data.job_title}'), 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, _safe(f'Candidat : {analysis_data.cv_filename}'), 0, 1)
    pdf.ln(3)

    # ── Score + verdict (2 cellules simples côte à côte) ──────────
    score = data.get('score', 'N/A')
    recommendation = data.get('hiring_recommendation', '')
    rec_colors = {
        'Fortement recommande': (34, 197, 94),
        'Recommande': (132, 204, 22),
        'A considerer': (245, 158, 11),
        'Non recommande': (239, 68, 68),
    }
    rec_key = _safe(recommendation).replace('e\x301', 'e').replace('\xe9', 'e').replace('\xe8', 'e').replace('\xc0', 'A')
    r, g, b = rec_colors.get(rec_key, (100, 100, 100))

    pdf.set_x(pdf.l_margin)
    pdf.set_fill_color(230, 244, 255)
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(0, 86, 179)
    pdf.cell(85, 14, _safe(f'Score : {score}%'), 0, 0, 'C', fill=True)
    pdf.set_fill_color(r, g, b)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(100, 14, _safe(recommendation)[:50], 0, 1, 'C', fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_x(pdf.l_margin)
    pdf.ln(2)

    justif = data.get('score_justification', '')
    if justif:
        pdf.set_x(pdf.l_margin)
        pdf.set_font('Arial', 'I', 9)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin, 5, _safe(f'Justification : {justif}'))
        pdf.set_text_color(0, 0, 0)
        pdf.set_x(pdf.l_margin)
    pdf.ln(3)

    # ── Profil candidat ────────────────────────────────────────────
    pdf.section_title('Profil du Candidat')
    pdf.key_value('Niveau de seniorite', data.get('seniority_level', 'N/A'))
    pdf.key_value("Annees d'experience", str(data.get('years_of_experience', 'N/A')))
    pdf.key_value("Ecart d'experience", data.get('experience_gap', 'N/A'))
    pdf.ln(3)

    # ── Résumé ─────────────────────────────────────────────────────
    pdf.section_title("Resume de l'Analyse")
    pdf.body_text(data.get('summary', ''))

    # ── Notation par catégorie ─────────────────────────────────────
    skills = data.get('skills_rating', {})
    if skills:
        pdf.section_title('Notation par Categorie (/10)')
        for category, note in skills.items():
            pdf.set_x(pdf.l_margin)
            pdf.set_font('Arial', '', 10)
            note_int = int(note) if isinstance(note, (int, float)) else 0
            bar_label = f'{note}/10  ' + ('|' * note_int) + ('.' * (10 - note_int))
            pdf.cell(0, 6, _safe(f'  {category} : {bar_label}'), 0, 1)
        pdf.ln(3)

    # ── Points forts ───────────────────────────────────────────────
    strengths = data.get('strengths', [])
    if strengths:
        pdf.section_title('Points Forts', r=21, g=128, b=61)
        pdf.bullet_list(strengths)

    # ── Axes d'amélioration ────────────────────────────────────────
    improvements = data.get('improvements', [])
    if improvements:
        pdf.section_title("Axes d'Amelioration", r=180, g=83, b=9)
        pdf.bullet_list(improvements)

    # ── Red flags ─────────────────────────────────────────────────
    red_flags = [f for f in data.get('red_flags', []) if 'aucun' not in f.lower()]
    if red_flags:
        pdf.section_title('Points de Vigilance', r=185, g=28, b=28)
        pdf.bullet_list(red_flags)

    # ── Lacunes techniques ─────────────────────────────────────────
    tech_gaps = data.get('technical_gaps', [])
    if tech_gaps:
        pdf.section_title('Lacunes Techniques', r=100, g=20, b=140)
        pdf.bullet_list(tech_gaps)

    # ── Mots-clés ──────────────────────────────────────────────────
    pdf.section_title('Mots-cles')
    matching = data.get('matching_keywords', [])
    missing = data.get('missing_keywords', [])
    if matching:
        pdf.set_x(pdf.l_margin)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 6, 'Presents dans le CV :', 0, 1)
        pdf.body_text(', '.join(matching))
    if missing:
        pdf.set_x(pdf.l_margin)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 6, 'Absents du CV :', 0, 1)
        pdf.body_text(', '.join(missing))

    # ── Conseils lettre de motivation ──────────────────────────────
    cover_tips = data.get('cover_letter_tips', [])
    if cover_tips:
        pdf.section_title('Conseils Lettre de Motivation')
        pdf.bullet_list(cover_tips)

    # ── Postes alternatifs ─────────────────────────────────────────
    alt_jobs = data.get('alternative_jobs', [])
    if alt_jobs:
        pdf.section_title('Postes Alternatifs Suggeres')
        pdf.bullet_list(alt_jobs)

    # ── Questions d'entretien ──────────────────────────────────────
    questions = data.get('interview_questions', [])
    if questions:
        pdf.add_page()
        pdf.section_title("Questions d'Entretien Suggerees")
        w = pdf.w - pdf.l_margin - pdf.r_margin
        for i, q in enumerate(questions, 1):
            pdf.set_x(pdf.l_margin)
            if isinstance(q, str):
                pdf.set_font('Arial', 'B', 10)
                pdf.multi_cell(w, 6, _safe(f'Q{i}. {q}'))
            elif isinstance(q, dict):
                pdf.set_font('Arial', 'B', 10)
                pdf.multi_cell(w, 6, _safe(f'Q{i}. {q.get("question", "")}'))
                if q.get('objectif'):
                    pdf.set_x(pdf.l_margin)
                    pdf.set_font('Arial', 'I', 9)
                    pdf.set_text_color(80, 80, 80)
                    pdf.multi_cell(w, 5, _safe(f'  Objectif : {q["objectif"]}'))
                    pdf.set_text_color(0, 0, 0)
                if q.get('reponse_attendue'):
                    pdf.set_x(pdf.l_margin)
                    pdf.set_font('Arial', 'B', 9)
                    pdf.cell(0, 5, '  Reponse attendue :', 0, 1)
                    pdf.set_x(pdf.l_margin)
                    pdf.set_font('Arial', '', 9)
                    pdf.multi_cell(w, 5, _safe(f'  {q["reponse_attendue"]}'))
                if q.get('conseil_recruteur'):
                    pdf.set_x(pdf.l_margin)
                    pdf.set_font('Arial', 'I', 9)
                    pdf.set_text_color(140, 80, 0)
                    pdf.multi_cell(w, 5, _safe(f'  Conseil : {q["conseil_recruteur"]}'))
                    pdf.set_text_color(0, 0, 0)
            pdf.set_x(pdf.l_margin)
            pdf.ln(4)

    pdf_bytes = bytes(pdf.output())
    return Response(
        content=pdf_bytes,
        media_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="rapport_analyse_{analysis_data.id}.pdf"'}
    )


def _safe(text: str) -> str:
    """Encode safely to latin-1 for fpdf."""
    if not isinstance(text, str):
        text = str(text)
    return text.encode('latin-1', 'replace').decode('latin-1')

class PDF(FPDF):
    def header(self):
        self.set_fill_color(30, 41, 59)
        self.rect(0, 0, 210, 22, 'F')
        self.set_font('Arial', 'B', 14)
        self.set_text_color(255, 255, 255)
        self.set_y(6)
        self.cell(0, 10, _safe('Rapport d\'Analyse de CV — Analyseur Intelligent'), 0, 1, 'C')
        self.set_text_color(0, 0, 0)
        self.ln(6)

    def footer(self):
        self.set_y(-12)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def section_title(self, title: str, r=30, g=41, b=59):
        self.set_fill_color(r, g, b)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 11)
        self.cell(0, 8, _safe(f'  {title}'), 0, 1, 'L', fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def body_text(self, text: str):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, _safe(text))
        self.ln(1)

    def bullet_list(self, items: list):
        self.set_font('Arial', '', 10)
        for item in items:
            self.multi_cell(0, 5, _safe(f'  • {item}'))
        self.ln(2)

    def key_value(self, key: str, value: str):
        self.set_font('Arial', 'B', 10)
        self.cell(65, 6, _safe(f'{key} :'), 0, 0)
        self.set_font('Arial', '', 10)
        self.cell(0, 6, _safe(str(value)[:120]), 0, 1)


def generate_pdf_report(analysis_data) -> Response:
    data = analysis_data.analysis_data
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── En-tête identité ───────────────────────────────────────────
    pdf.set_font('Arial', 'B', 13)
    pdf.cell(0, 8, _safe(f'Poste : {analysis_data.job_title}'), 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, _safe(f'Candidat : {analysis_data.cv_filename}'), 0, 1)
    pdf.ln(3)

    # ── Score + verdict ────────────────────────────────────────────
    score = data.get('score', 'N/A')
    recommendation = data.get('hiring_recommendation', '')
    rec_colors = {
        'Fortement recommande': (34, 197, 94),
        'Recommande': (132, 204, 22),
        'A considerer': (245, 158, 11),
        'Non recommande': (239, 68, 68),
    }
    rec_key = _safe(recommendation).replace('é', 'e').replace('è', 'e').replace('À', 'A')
    r, g, b = rec_colors.get(rec_key, (100, 100, 100))

    pdf.set_fill_color(240, 249, 255)
    pdf.set_draw_color(147, 197, 253)
    pdf.rect(10, pdf.get_y(), 90, 22, 'FD')
    pdf.set_xy(12, pdf.get_y() + 3)
    pdf.set_font('Arial', 'B', 22)
    pdf.set_text_color(0, 86, 179)
    pdf.cell(86, 10, f'{score}%', 0, 0, 'C')

    pdf.set_xy(105, pdf.get_y() - 7)
    pdf.set_fill_color(r, g, b)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(90, 16, _safe(recommendation), 0, 0, 'C', fill=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(22)

    justif = data.get('score_justification', '')
    if justif:
        pdf.set_font('Arial', 'I', 9)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(0, 5, _safe(f'Justification : {justif}'))
        pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    # ── Profil candidat ────────────────────────────────────────────
    pdf.section_title('Profil du Candidat')
    pdf.key_value('Niveau de seniorite', data.get('seniority_level', 'N/A'))
    pdf.key_value("Annees d'experience", str(data.get('years_of_experience', 'N/A')))
    pdf.key_value("Ecart d'experience", data.get('experience_gap', 'N/A'))
    pdf.ln(3)

    # ── Résumé ─────────────────────────────────────────────────────
    pdf.section_title('Resume de l\'Analyse')
    pdf.body_text(data.get('summary', ''))

    # ── Notation par catégorie ─────────────────────────────────────
    skills = data.get('skills_rating', {})
    if skills:
        pdf.section_title('Notation par Categorie (/10)')
        for category, note in skills.items():
            pdf.set_font('Arial', '', 10)
            pdf.cell(90, 6, _safe(f'  {category}'), 0, 0)
            bar_width = int(note) * 9
            pdf.set_fill_color(59, 130, 246)
            pdf.rect(pdf.get_x(), pdf.get_y() + 1, bar_width, 4, 'F')
            pdf.set_x(pdf.get_x() + 92)
            pdf.cell(10, 6, f'{note}/10', 0, 1)
        pdf.ln(3)

    # ── Points forts ───────────────────────────────────────────────
    strengths = data.get('strengths', [])
    if strengths:
        pdf.section_title('Points Forts', r=21, g=128, b=61)
        pdf.bullet_list(strengths)

    # ── Axes d'amélioration ────────────────────────────────────────
    improvements = data.get('improvements', [])
    if improvements:
        pdf.section_title('Axes d\'Amelioration', r=180, g=83, b=9)
        pdf.bullet_list(improvements)

    # ── Red flags ─────────────────────────────────────────────────
    red_flags = [f for f in data.get('red_flags', []) if 'aucun' not in f.lower()]
    if red_flags:
        pdf.section_title('Points de Vigilance', r=185, g=28, b=28)
        pdf.bullet_list(red_flags)

    # ── Lacunes techniques ─────────────────────────────────────────
    tech_gaps = data.get('technical_gaps', [])
    if tech_gaps:
        pdf.section_title('Lacunes Techniques', r=100, g=20, b=140)
        pdf.bullet_list(tech_gaps)

    # ── Mots-clés ──────────────────────────────────────────────────
    pdf.section_title('Mots-cles')
    matching = data.get('matching_keywords', [])
    missing = data.get('missing_keywords', [])
    if matching:
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 6, _safe('Presents dans le CV :'), 0, 1)
        pdf.body_text(', '.join(matching))
    if missing:
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 6, _safe('Absents du CV :'), 0, 1)
        pdf.body_text(', '.join(missing))

    # ── Conseils lettre de motivation ──────────────────────────────
    cover_tips = data.get('cover_letter_tips', [])
    if cover_tips:
        pdf.section_title('Conseils Lettre de Motivation')
        pdf.bullet_list(cover_tips)

    # ── Postes alternatifs ─────────────────────────────────────────
    alt_jobs = data.get('alternative_jobs', [])
    if alt_jobs:
        pdf.section_title('Postes Alternatifs Suggeres')
        pdf.bullet_list(alt_jobs)

    # ── Questions d'entretien ──────────────────────────────────────
    questions = data.get('interview_questions', [])
    if questions:
        pdf.add_page()
        pdf.section_title('Questions d\'Entretien Suggerees (avec reponses)')
        for i, q in enumerate(questions, 1):
            if isinstance(q, str):
                pdf.set_font('Arial', 'B', 10)
                pdf.multi_cell(0, 6, _safe(f'Q{i}. {q}'))
                pdf.ln(2)
            elif isinstance(q, dict):
                pdf.set_fill_color(240, 245, 255)
                pdf.set_font('Arial', 'B', 10)
                pdf.multi_cell(0, 6, _safe(f'Q{i}. {q.get("question", "")}'), fill=True)
                if q.get('objectif'):
                    pdf.set_font('Arial', 'BI', 9)
                    pdf.set_text_color(80, 80, 80)
                    pdf.multi_cell(0, 5, _safe(f'  Objectif : {q["objectif"]}'))
                    pdf.set_text_color(0, 0, 0)
                if q.get('reponse_attendue'):
                    pdf.set_font('Arial', 'B', 9)
                    pdf.cell(0, 5, _safe('  Reponse attendue :'), 0, 1)
                    pdf.set_font('Arial', '', 9)
                    pdf.multi_cell(0, 5, _safe(f'  {q["reponse_attendue"]}'))
                if q.get('conseil_recruteur'):
                    pdf.set_font('Arial', 'BI', 9)
                    pdf.set_text_color(120, 60, 0)
                    pdf.multi_cell(0, 5, _safe(f'  Conseil recruteur : {q["conseil_recruteur"]}'))
                    pdf.set_text_color(0, 0, 0)
                pdf.ln(4)

    pdf_bytes = bytes(pdf.output())
    return Response(
        content=pdf_bytes,
        media_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="rapport_analyse_{analysis_data.id}.pdf"'}
    )
