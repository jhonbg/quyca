import io
from unittest.mock import patch

"""
Helper function to authenticate a test user and return a valid JWT token.
"""


def get_auth_token(client):
    response = client.post("/app/login", json={"email": "test@test.com", "password": "123456"})
    assert response.status_code == 200, f"Login falló: {response.json}"
    return response.json["access_token"]


def test_staff_upload_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}

    response = client.post(
        "/app/submit/staff",
        headers=headers,
        data={"file": (io.BytesIO(b"excel-content"), "staff.xlsx")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 401
    assert response.json["msg"] in ["Token inválido o expirado", "Token no encontrado en headers"]


def test_staff_upload_with_invalid_columns(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    with patch("quyca.application.routes.app.staff_app_router.StaffService.handle_staff_upload") as mock_service:
        mock_service.return_value = (
            {
                "success": False,
                "errores": 1,
                "duplicados": 0,
                "msg": "El archivo enviado no cumple con el formato requerido de columnas",
                "detalles": ["Columna sin nombre en posición 20"],
            },
            422,
        )

        data = {"file": (io.BytesIO(b"excel-content"), "staff.xlsx")}
        response = client.post("/app/submit/staff", headers=headers, data=data, content_type="multipart/form-data")

        assert response.status_code == 422
        assert response.json["success"] is False
        assert response.json["msg"].startswith("El archivo enviado no cumple con el formato requerido")


def test_staff_upload_empty_file(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    with patch("quyca.application.routes.app.staff_app_router.StaffService.handle_staff_upload") as mock_service:
        mock_service.return_value = (
            {"success": False, "msg": "El archivo cargado está vacío. Verifique que contenga información."},
            400,
        )

        data = {"file": (io.BytesIO(b""), "staff.xlsx")}
        response = client.post("/app/submit/staff", headers=headers, data=data, content_type="multipart/form-data")

        assert response.status_code == 400
        assert response.json["msg"] == "El archivo cargado está vacío. Verifique que contenga información."


def test_staff_upload_success(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    with patch("quyca.application.routes.app.staff_app_router.StaffService.handle_staff_upload") as mock_service:
        mock_service.return_value = (
            {"success": True, "errores": 0, "duplicados": 1, "pdf_base64": "JVBERi0xLjQKJ..."},
            200,
        )

        data = {"file": (io.BytesIO(b"excel-content"), "staff.xlsx")}
        response = client.post("/app/submit/staff", headers=headers, data=data, content_type="multipart/form-data")

        assert response.status_code == 200
        assert response.json["success"] is True


def test_staff_upload_no_file(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/app/submit/staff", headers=headers, data={})

    assert response.status_code == 400
    assert response.json["success"] is False
    assert response.json["msg"] == "Archivo requerido"


def test_staff_upload_with_errors(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    with patch("quyca.application.routes.app.staff_app_router.StaffService.handle_staff_upload") as mock_service:
        mock_service.return_value = (
            {"success": False, "errores": 3, "duplicados": 0, "pdf_base64": "JVBERi0xLjQKJ..."},
            400,
        )

        data = {"file": (io.BytesIO(b"excel-content"), "staff.xlsx")}
        response = client.post("/app/submit/staff", headers=headers, data=data, content_type="multipart/form-data")

        assert response.status_code == 400
        assert response.json["success"] is False
        assert response.json["errores"] == 3


def test_staff_upload_with_duplicates(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    with patch("quyca.application.routes.app.staff_app_router.StaffService.handle_staff_upload") as mock_service:
        mock_service.return_value = (
            {"success": True, "errores": 0, "duplicados": 2, "pdf_base64": "JVBERi0xLjQKJ..."},
            200,
        )

        data = {"file": (io.BytesIO(b"excel-with-duplicates"), "staff.xlsx")}
        response = client.post("/app/submit/staff", headers=headers, data=data, content_type="multipart/form-data")

        assert response.status_code == 200
        assert response.json["duplicados"] == 2


def test_staff_upload_email_failed(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    with patch("quyca.application.routes.app.staff_app_router.StaffService.handle_staff_upload") as mock_service:
        mock_service.return_value = ({"success": False, "msg": "Fallo al enviar correo"}, 500)

        data = {"file": (io.BytesIO(b"excel-content"), "staff.xlsx")}
        response = client.post("/app/submit/staff", headers=headers, data=data, content_type="multipart/form-data")

        assert response.status_code == 500
        assert response.json["success"] is False


def test_file_repository_fallback_local(tmp_path):
    from quyca.infrastructure.repositories.file_repository import FileRepository

    class DummyDriveRepo:
        def get_or_create_folder(self, *args, **kwargs):
            raise Exception("Drive unavailable")

        def upload_file(self, *args, **kwargs):
            raise Exception("Drive unavailable")

    file_repo = FileRepository(DummyDriveRepo())

    class DummyFile:
        def save(self, path):
            with open(path, "wb") as f:
                f.write(b"test content")

    import flask

    app = flask.Flask(__name__)
    app.config["LOCAL_STORAGE_PATH"] = str(tmp_path)

    with app.app_context():
        result = file_repo.save_file(DummyFile(), "123", "TestInstitution", "staff")

    assert result["success"] is True
    assert "almacenamiento local" in result["msg"]

    files = list(tmp_path.rglob("*"))
    assert any("staff" in str(f) for f in files)
