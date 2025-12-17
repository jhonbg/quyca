import io
from unittest.mock import patch

"""
Helper function to authenticate a test user and return a valid JWT token.
"""


def get_auth_token(client):
    response = client.post(
        "/app/login",
        json={"email": "test@test.com", "password": "123456"},
    )
    assert response.status_code == 200, f"Login failed: {response.json}"
    return response.json["access_token"]


def test_scienti_upload_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}

    response = client.post(
        "/app/submit/scienti",
        headers=headers,
        data={"file": (io.BytesIO(b"zip-content"), "data.zip")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 401
    assert response.json["success"] is False


def test_scienti_upload_invalid_jwt(client):
    headers = {"Authorization": "Bearer invalid_token"}

    response = client.post(
        "/app/submit/scienti",
        headers=headers,
        data={"file": (io.BytesIO(b"zip-content"), "data.zip")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 401
    assert response.json["msg"] == "Token inválido o expirado"


def test_scienti_upload_missing_authorization_header(client):
    response = client.post(
        "/app/submit/scienti",
        data={"file": (io.BytesIO(b"zip-content"), "data.zip")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 401
    assert response.json["msg"] == "Token inválido o expirado"


def test_scienti_upload_no_file(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/app/submit/scienti",
        headers=headers,
        data={},
    )

    assert response.status_code == 400
    assert response.json["msg"] == "Archivo requerido"


def test_scienti_upload_empty_filename(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    data = {"file": (io.BytesIO(b"zip-content"), "")}
    response = client.post(
        "/app/submit/scienti",
        headers=headers,
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.json["msg"] == "No se seleccionó ningún archivo"


def test_scienti_upload_invalid_extension(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    data = {"file": (io.BytesIO(b"data"), "file.txt")}
    response = client.post(
        "/app/submit/scienti",
        headers=headers,
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 415
    assert response.json["success"] is False


def test_scienti_upload_success(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    with patch("quyca.application.routes.app.scienti_app_router.ScientiService.handle_scienti_upload") as mock_service:
        mock_service.return_value = (
            {
                "success": True,
                "msg": "Archivo SCIENTI recibido con éxito para ser validado.",
                "filename": "data.zip",
                "upload_date": "01/01/2025 10:00",
                "file_msg": "Archivo guardado correctamente",
            },
            200,
        )

        data = {"file": (io.BytesIO(b"zip-content"), "data.zip")}
        response = client.post(
            "/app/submit/scienti",
            headers=headers,
            data=data,
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        assert response.json["success"] is True
        assert response.json["filename"] == "data.zip"
