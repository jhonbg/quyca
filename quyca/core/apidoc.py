from os import getenv


def generate_apidoc():
    command = (
        "apidoc -i /quyca/routes "
        f"-c /quyca/core/docs/apidoc.{getenv('ENVIRONMENT', 'dev')}.json "
        "-o /quyca/core/docs/apidoc"
    )
