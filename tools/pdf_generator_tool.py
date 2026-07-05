"""
PDF Generator Tool

Renders complaint letter text into a PDF document using ReportLab.
Called by the orchestrator's after_action node (not by an LLM agent directly).
"""

import os
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_complaint_pdf(complaint_text: str) -> str:
    """Generate a PDF document from the complaint letter text.

    Args:
        complaint_text: Full text of the complaint letter.

    Returns:
        File path to the generated PDF, or empty string on failure.
    """
    try:
        os.makedirs("data/generated_docs", exist_ok=True)
        file_name = f"data/generated_docs/complaint_{uuid.uuid4().hex[:8]}.pdf"

        c = canvas.Canvas(file_name, pagesize=letter)
        width, height = letter

        text_obj = c.beginText(50, height - 50)
        text_obj.setFont("Helvetica", 10)

        for line in complaint_text.split("\n"):
            # Word-wrap each line at ~90 characters
            current = ""
            for word in line.split(" "):
                if len(current) + len(word) < 90:
                    current += word + " "
                else:
                    text_obj.textLine(current.rstrip())
                    current = word + " "
            if current:
                text_obj.textLine(current.rstrip())

            # Start a new page if we're near the bottom
            if text_obj.getY() < 50:
                c.drawText(text_obj)
                c.showPage()
                text_obj = c.beginText(50, height - 50)
                text_obj.setFont("Helvetica", 10)

        c.drawText(text_obj)
        c.save()
        return file_name

    except Exception as e:
        print(f"PDF generation error: {e}")
        return ""
