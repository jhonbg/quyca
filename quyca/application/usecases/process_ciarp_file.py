import io
import pandas as pd
import base64
from domain.validators.ciarp_validator import CiarpValidator
from domain.services.staff_report_service import StaffReportService
from infrastructure.notifications.staff_notification import StaffNotification

class ProcessCiarpFileUseCase:
    def __init__(self, report_service: StaffReportService, notification_service: StaffNotification):
        self.report_service = report_service
        self.notification_service = notification_service
        
    def execute(self, file: io.BytesIO, institution: str, filename: str, upload_date: str, user: str, email: str) -> dict:
        df = pd.read_excel(file)
        valid, errors_columns, _ = CiarpValidator.validate_columns(df)
        if not valid:
            return {
                "success": False,
                "msg": "El archivo enviado no cumple con el formato requerido de columnas",
                "detalles": errors_columns,
            }
            
        report, attachments = self.report_service.generate_report(df, institution, filename, upload_date, user)
        self.notification_service.send_report(report, institution, filename, upload_date, user, email, attachments)
        
        pdf_base64 = None
        for att in attachments:
            if att["filename"].endswith(".pdf"):
                pdf_base64 = base64.b64encode(att["bytes"].read()).decode()
                break
        
        return{
            "success": report.total_errores == 0,
            "errores": report.total_errores,
            "pdf_base64": pdf_base64
        }