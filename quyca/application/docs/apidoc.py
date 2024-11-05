from os import getenv


def generate_apidoc() -> None:
    command = (
        "apidoc -i ./quyca/application/routes -c ./quyca/application/docs/apidoc.dev.json -o ./quyca/application/static"
    )
