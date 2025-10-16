from infrastructure.repositories.gmail_repository import GmailRepository
from infrastructure.email_templates.staff_report_templates import build_email_template
from domain.models.staff_report_model import StaffReport

"""
Service responsible for sending validation reports via email.
Uses a GmailRepository to deliver messages with context-aware templates
based on the validation outcome (accepted, warnings, or rejected).
Currently used for staff and CIARP reports.
"""


class StaffNotification:
    def __init__(self, gmail_repo: GmailRepository):
        self.gmail_repo = gmail_repo

    def send_report(
        self,
        staff_report: StaffReport,
        institution: str,
        filename: str,
        upload_date: str,
        user: str,
        email: str,
        attachments: list[dict],
    ) -> dict:
        tipo_correo = (
            "rechazado"
            if staff_report.total_errores > 0
            else ("advertencias" if len(staff_report.advertencias) > 0 else "aceptado")
        )

        subject, body_html = build_email_template(
            tipo=tipo_correo, rol=user, institution=institution, filename=filename, upload_date=upload_date
        )

        return self.gmail_repo.send_email(to_email=email, subject=subject, body_html=body_html, attachments=attachments)
