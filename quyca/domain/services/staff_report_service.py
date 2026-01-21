import io
import pandas as pd
from quyca.domain.models.staff_report_model import StaffReport
from quyca.domain.repositories.dataframe_annotator_interface import IDataFrameAnnotator
from quyca.domain.repositories.pdf_repository_interface import IPDFRepository
from quyca.domain.repositories.xlsx_exporter_interface import IXlsxExporter
from quyca.domain.validators.staff_validator import StaffValidator


class StaffReportService:
    """Generates report files (PDF + Excel) from validation results."""

    def __init__(
        self,
        pdf_repo: IPDFRepository,
        annotator: IDataFrameAnnotator,
        xlsx_exporter: IXlsxExporter,
    ):
        self.pdf_repo = pdf_repo
        self.annotator = annotator
        self.xlsx_exporter = xlsx_exporter

    def generate_report(
        self, df: pd.DataFrame, institution: str, filename: str, upload_date: str, user: str
    ) -> tuple[StaffReport, list[dict]]:
        staff_report: StaffReport = StaffValidator.validate_dataframe(df)

        attachments: list[dict] = []
        pdf_bytes: io.BytesIO | None = None

        if staff_report.total_errores > 0 or len(staff_report.advertencias) > 0 or staff_report.total_duplicados > 0:
            pdf_bytes = self.pdf_repo.generate_quality_report(
                staff_report.errores_agrupados,
                staff_report.advertencias_agrupadas,
                staff_report.duplicados,
                institution,
                filename,
                upload_date,
                user,
            )

            attachments = [{"bytes": pdf_bytes, "filename": "reporte_staff.pdf", "mime": "application/pdf"}]

            annotated_df = self.annotator.annotate(df, staff_report)
            excel_bytes = self.xlsx_exporter.to_excel_bytes(annotated_df)

            attachments.append(
                {
                    "bytes": excel_bytes,
                    "filename": "staff_validado.xlsx",
                    "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                }
            )

        return staff_report, attachments
