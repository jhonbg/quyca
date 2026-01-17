from flask_jwt_extended import create_access_token, decode_token


class JwtTokenService:
    def create_access_token(self, subject: str, claims: dict) -> str:
        return create_access_token(identity=subject, additional_claims=claims)

    def decode(self, token: str) -> dict:
        return decode_token(token)
