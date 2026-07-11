from datetime import datetime
from io import BytesIO
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from studymate_rag.core.config import Settings


class ExportService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def export_markdown(self, title: str, body: str) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self._slug(title)}_{timestamp}.md"
        path = self.settings.export_dir / filename
        path.write_text(f"# {title}\n\n{body.strip()}\n", encoding="utf-8")
        return path

    def pdf_bytes(self, title: str, body: str) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, title=title)
        styles = getSampleStyleSheet()
        story = [Paragraph(title, styles["Title"]), Spacer(1, 12)]
        for block in body.strip().split("\n"):
            text = block.strip() or " "
            story.append(Paragraph(self._escape(text), styles["BodyText"]))
            story.append(Spacer(1, 6))
        doc.build(story)
        return buffer.getvalue()

    def _slug(self, value: str) -> str:
        cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value)
        return "-".join(part for part in cleaned.split("-") if part)[:60] or "export"

    def _escape(self, value: str) -> str:
        return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
