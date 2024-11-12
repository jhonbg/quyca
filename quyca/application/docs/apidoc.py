def generate_apidoc() -> None:
    command = "apidoc -i ./quyca/application/routes -c ./quyca/application/docs/apidoc.prod.json -o ./quyca/application/static"
