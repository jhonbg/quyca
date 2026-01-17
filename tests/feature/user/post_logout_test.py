from typing import Any
from unittest.mock import patch


def test_logout_success(client: Any) -> None:
    """Should return 200 and success=True when the token is valid"""
    token = "fake-jwt-token"

    with patch(
        "quyca.application.routes.app.user_auth_app_router.LogoutUserUseCase.execute",
        return_value={"success": True, "msg": "Sesión cerrada correctamente"},
    ) as mock_logout_user:
        mock_logout_user.return_value = {"success": True, "msg": "Logged out"}

        response = client.post(
            "/app/logout",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json["success"] is True
        mock_logout_user.assert_called_once_with(token)


def test_logout_invalid_token(client: Any) -> None:
    """Should return 401 and success=False when the token is invalid"""
    token = "fake-jwt-token"

    with patch(
        "quyca.application.routes.app.user_auth_app_router.LogoutUserUseCase.execute",
        return_value={"success": False, "msg": "Token inválido o caducado"},
    ) as mock_logout_user:
        mock_logout_user.return_value = {"success": False, "msg": "Token inválido"}

        response = client.post(
            "/app/logout",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401
        assert response.json["success"] is False
        assert "msg" in response.json
        mock_logout_user.assert_called_once_with(token)


def test_logout_no_token(client: Any) -> None:
    """Should return 400 when no token is sent in the request"""
    response = client.post("/app/logout")

    assert response.status_code == 401
    assert response.json["success"] is False
    assert response.json["msg"] == "Token requerido"
