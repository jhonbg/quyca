from typing import Tuple
from quyca.application.usecases.login_user import LoginUserUseCase
from quyca.infrastructure.security.jwt_token_service import JwtTokenService
from quyca.infrastructure.repositories.pdf_repository import PDFRepository
from quyca.infrastructure.repositories.gmail_repository import GmailRepository
from quyca.infrastructure.repositories.google_drive_repository import GoogleDriveRepository
from quyca.infrastructure.repositories.file_repository import FileRepository
from quyca.infrastructure.notifications.notification import StaffNotification
from quyca.application.usecases.process_staff_file import ProcessStaffFileUseCase
from quyca.application.usecases.process_ciarp_file import ProcessCiarpFileUseCase
from quyca.application.usecases.save_staff_file import SaveStaffFileUseCase
from quyca.application.usecases.save_ciarp_file import SaveCiarpFileUseCase
from quyca.application.usecases.save_scienti_file import SaveScientiFileUseCase
from quyca.domain.services.scienti_service import ScientiService
from quyca.domain.services.staff_report_service import StaffReportService
from quyca.domain.services.ciarp_report_service import CiarpReportService
from quyca.infrastructure.repositories.user_repository import UserRepositoryMongo

"""
DI composer for Staff: builds infrastructure, use cases and service.
"""

"""
Builds and wires dependencies for the Staff service.
"""


def build_staff_service() -> Tuple[ProcessStaffFileUseCase, SaveStaffFileUseCase, UserRepositoryMongo]:
    pdf_repo = PDFRepository()
    gmail_repo = GmailRepository()
    drive_repo = GoogleDriveRepository()
    file_repo = FileRepository(drive_repo)

    report_service = StaffReportService(pdf_repo, gmail_repo)
    notification_service = StaffNotification(gmail_repo)

    process_usecase = ProcessStaffFileUseCase(report_service, notification_service)
    save_usecase = SaveStaffFileUseCase(file_repo)
    user_repo = UserRepositoryMongo()

    return process_usecase, save_usecase, user_repo


"""
Builds and wires dependencies for the CIARP service.
"""


def build_ciarp_service() -> Tuple[ProcessCiarpFileUseCase, SaveCiarpFileUseCase, UserRepositoryMongo]:
    pdf_repo = PDFRepository()
    gmail_repo = GmailRepository()
    drive_repo = GoogleDriveRepository()
    file_repo = FileRepository(drive_repo)

    report_service = CiarpReportService(pdf_repo, gmail_repo)
    notification_service = StaffNotification(gmail_repo)

    process_usecase = ProcessCiarpFileUseCase(report_service, notification_service)
    save_usecase = SaveCiarpFileUseCase(file_repo)
    user_repo = UserRepositoryMongo()

    return process_usecase, save_usecase, user_repo


"""
ScientiService builder for dependency injection.
"""


def build_scienti_service() -> ScientiService:
    gmail_repo = GmailRepository()
    drive_repo = GoogleDriveRepository()
    file_repo = FileRepository(drive_repo)

    notification = StaffNotification(gmail_repo)
    save_usecase = SaveScientiFileUseCase(file_repo)
    user_repo = UserRepositoryMongo()

    return ScientiService(notification=notification, save_usecase=save_usecase, user_repo=user_repo)


def build_login_usecase() -> LoginUserUseCase:
    return LoginUserUseCase(user_repo=UserRepositoryMongo(), token_service=JwtTokenService())
