from typing import Tuple
from flask import Blueprint, request, jsonify, Response, current_app
from sentry_sdk import capture_exception

from flask_jwt_extended import set_access_cookies, unset_jwt_cookies

from quyca.domain.exceptions.not_entity_exception import NotEntityException
from quyca.infrastructure.repositories.user_repository import UserRepositoryMongo
from quyca.infrastructure.security.jwt_token_service import JwtTokenService
from quyca.application.usecases.login_user import LoginUserUseCase
from quyca.application.usecases.logout_user import LogoutUserUseCase

user_auth_app_router = Blueprint("user_auth_app_router", __name__)

"""
@api {post} /app/login
@apiName PostLoginUser
@apiGroup Authentication
@apiVersion 1.0.0
@apiDescription Allows authenticating a user using their email and password.
If the credentials are valid, it returns a JWT token along with the user's role.

@apiBody {String} email User email.
@apiBody {String} password User password.

@apiSuccess {Boolean} success Indicates whether the authentication was successful.
@apiSuccess {String} rorID ID number associated with the entity.
@apiSuccess {String} access_token Generated JWT token.

@apiSuccessExample {json} Successful Response:
HTTP/1.1 200 OK
{
    "success": true,
    "rorID": "admin",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR..."
}

@apiError {Boolean} success Indicates that authentication failed.
@apiError {String} msg Error message.

@apiErrorExample {json} Error Response - Invalid Credentials:
HTTP/1.1 401 Unauthorized
{
    "success": false
}

@apiErrorExample {json} Error Response - Missing Fields:
HTTP/1.1 400 Bad Request
{
    "success": false,
    "msg": "email and password are required"
}
"""

"""
@api {post} /app/logout
@apiName PostLogoutUser
@apiGroup Authentication
@apiVersion 1.0.0
@apiDescription Allows logging out a user by invalidating their JWT token.  
If the token is valid, it is removed from the database.

@apiBody {String} token JWT token to be invalidated.

@apiSuccess {Boolean} success Indicates whether the logout was successful.
@apiSuccess {String} msg Confirmation message.

@apiSuccessExample {json} Successful Response:
HTTP/1.1 200 OK
{
    "success": true,
    "msg": "Session closed successfully"
}
"""


@user_auth_app_router.route("/login", methods=["POST"])
def login() -> Tuple[Response, int]:
    try:
        data = request.get_json(force=True) or {}
        email = (data.get("email") or "").strip()
        password = data.get("password") or ""

        if not email or not password:
            return jsonify({"success": False, "msg": "correo y contraseña requeridos"}), 400

        repo = UserRepositoryMongo()
        token_service = JwtTokenService()
        usecase = LoginUserUseCase(user_repo=repo, token_service=token_service)

        result = usecase.execute(email, password)

        status_code = 200 if result.get("success") else 401

        token = result.get("access_token", "")
        response_body = {**result}

        response_body.pop("access_token", None)

        response = jsonify(response_body)
        if status_code == 200 and token:
            set_access_cookies(response, token)

        return response, status_code

    except NotEntityException as e:
        return jsonify({"success": False, "msg": str(e)}), 404

    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": str(e)}), 500


"""
@api {post} /app/logout
@apiName PostLogoutUser
@apiGroup Authentication
@apiVersion 1.0.0
@apiDescription Allows logging out a user by invalidating their JWT token.  
If the token is valid, it is removed from the database.

@apiBody {String} token JWT token to be invalidated.

@apiSuccess {Boolean} success Indicates whether the logout was successful.
@apiSuccess {String} msg Confirmation message.

@apiSuccessExample {json} Successful Response:
HTTP/1.1 200 OK
{
    "success": true,
    "msg": "Session closed successfully"
}
"""


@user_auth_app_router.route("/logout", methods=["POST"])
def logout() -> Tuple[Response, int]:
    try:
        cookie_name = current_app.config.get("JWT_ACCESS_COOKIE_NAME", "access_token_cookie")
        token = request.cookies.get(cookie_name, "")

        if not token:
            result = {"success": False, "msg": "No hay sesión válida"}
            return jsonify(result), 401

        repo = UserRepositoryMongo()
        token_service = JwtTokenService()
        usecase = LogoutUserUseCase(repo, token_service)

        result = usecase.execute(token)

        status_code = 200 if result.get("success") else 401
        response = jsonify(result)

        if status_code == 200:
            unset_jwt_cookies(response)

        return response, status_code

    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": str(e)}), 500
