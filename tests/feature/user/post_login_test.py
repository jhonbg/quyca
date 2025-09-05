def test_login_success(client):
    response = client.post("/app/login", json={"email": "usuario@test.com", "password": "123456"})
    assert response.status_code == 200
    assert response.json["success"] is True
    assert "access_token" in response.json


def test_login_fail_invalid_password(client):
    response = client.post("/app/login", json={"email": "wrong@test.com", "password": "123456"})
    assert response.status_code == 401
    assert response.json["success"] is False
