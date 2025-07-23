from fpdf import FPDF
from fastapi.responses import Response

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Rapport d\'Analyse de CV', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 5, body.encode('latin-1', 'replace').decode('latin-1'))
        self.ln()

def generate_pdf_report(analysis_data) -> Response:
    pdf = PDF()
    pdf.add_page()
    data = analysis_data.analysis_data
    
    pdf.chapter_title(f"Analyse pour le poste : {analysis_data.job_title}")
    pdf.chapter_body(f"Candidat (CV) : {analysis_data.cv_filename}")

    pdf.chapter_title(f"Score d'adéquation : {data.get('score', 'N/A')}% ")
    pdf.chapter_body(data.get('summary', ''))

    pdf.chapter_title("Points forts")
    pdf.chapter_body('\n'.join(f"- {s}" for s in data.get('strengths', [])))

    pdf.chapter_title("Axes d'amélioration")
    pdf.chapter_body('\n'.join(f"- {i}" for i in data.get('improvements', [])))

    pdf.output(dest='S')
    pdf_bytes = pdf.buffer.encode('latin-1')

    return Response(content=pdf_bytes, media_type='application/pdf',
                    headers={'Content-Disposition': f'attachment; filename="rapport_{analysis_data.id}.pdf"'})