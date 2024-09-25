from os import getenv


def generate_apidoc() -> None:
    command = (
        "apidoc -i /quyca/routes " f"-c /quyca/core/docs/apidoc.{getenv('ENVIRONMENT', 'dev')}.json " "-o /quyca/static"
    )
