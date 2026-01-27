from typing import Any
from unittest.mock import Mock, patch, ANY

ROUTER_MOD = "quyca.application.routes.app.user_crud_app_router"


def _admin_headers() -> dict[str, str]:
    return {"Authorization": "Bearer fake.jwt.token"}


def test_create_user_no_token(client: Any) -> None:
    resp = client.post(
        "/app/admin/users/test@udea.edu.co",
        json={"institution": "UdeA", "ror_id": "R001", "role": "staff"},
    )
    assert resp.status_code == 401
    assert "Token" in resp.json["msg"]


def test_create_user_non_admin(client: Any) -> None:
    with patch(f"{ROUTER_MOD}.verify_jwt_in_request", return_value=True), patch(
        f"{ROUTER_MOD}.get_jwt", return_value={"role": "staff"}
    ):
        resp = client.post(
            "/app/admin/users/staff@udea.edu.co",
            headers=_admin_headers(),
            json={"institution": "UdeA", "ror_id": "R001", "role": "staff"},
        )
        assert resp.status_code == 403
        assert "Permiso denegado" in resp.json["msg"]


def test_create_user_success(client: Any) -> None:
    usecase_mock = Mock()
    usecase_mock.create_user.return_value = {"success": True, "msg": "Usuario creado correctamente."}

    with patch(f"{ROUTER_MOD}.verify_jwt_in_request", return_value=True), patch(
        f"{ROUTER_MOD}.get_jwt", return_value={"role": "admin"}
    ), patch(f"{ROUTER_MOD}.usecase", usecase_mock):
        resp = client.post(
            "/app/admin/users/ok@udea.edu.co",
            headers=_admin_headers(),
            json={"institution": "UdeA", "ror_id": "R100", "role": "staff"},
        )
        assert resp.status_code == 201
        assert resp.json["success"] is True
        assert "Usuario" in resp.json["msg"]
        usecase_mock.create_user.assert_called_once_with("ok@udea.edu.co", "UdeA", "R100", "staff", ANY)


def test_create_user_conflict(client: Any) -> None:
    usecase_mock = Mock()
    usecase_mock.create_user.return_value = {
        "success": False,
        "msg": "Ya existe un correo registrado para esa universidad",
    }

    with patch(f"{ROUTER_MOD}.verify_jwt_in_request", return_value=True), patch(
        f"{ROUTER_MOD}.get_jwt", return_value={"role": "admin"}
    ), patch(f"{ROUTER_MOD}.usecase", usecase_mock):
        resp = client.post(
            "/app/admin/users/dup@udea.edu.co",
            headers=_admin_headers(),
            json={"institution": "UdeA", "ror_id": "R001", "role": "staff"},
        )
        assert resp.status_code == 409
        assert resp.json["success"] is False
        assert "ya existe" in resp.json["msg"].lower()
        usecase_mock.create_user.assert_called_once_with("dup@udea.edu.co", "UdeA", "R001", "staff", ANY)
