from unittest.mock import patch, ANY


def test_logout_success(client):
    """Should return 200 and success=True when the token is valid"""
    token = "fake-jwt-token"

    with patch("quyca.application.routes.app.user_auth_app_router.auth_service.logout_user") as mock_logout_user:
        mock_logout_user.return_value = {"success": True, "msg": "Logged out"}

        response = client.post("/app/logout", json={"token": token})

        assert response.status_code == 200
        assert response.json["success"] is True
        mock_logout_user.assert_called_once_with(token, ANY)


def test_logout_invalid_token(client):
    """Should return 401 and success=False when the token is invalid"""
    token = "fake-jwt-token"

    with patch("quyca.application.routes.app.user_auth_app_router.auth_service.logout_user") as mock_logout_user:
        mock_logout_user.return_value = {"success": False, "msg": "Token inválido"}

        response = client.post("/app/logout", json={"token": token})

        assert response.status_code == 401
        assert response.json["success"] is False
        assert "msg" in response.json
        mock_logout_user.assert_called_once_with(token, ANY)


def test_logout_no_token(client):
    """Should return 400 when no token is sent in the request"""
    response = client.post("/app/logout", json={})

    assert response.status_code == 400
    assert response.json["success"] is False
    assert response.json["msg"] == "Token requerido"
