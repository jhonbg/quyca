import subprocess

from core.logging import get_logger

log = get_logger(__name__)


def generate_apidoc():
    log.debug("Generating API documentation")
    command = (
        "apidoc -i /usr/src/app/app/api/routes/v1 "
        "-c /usr/src/app/app/apidoc.json "
        "-o /usr/src/app/app/api/apidoc "
        
    )
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()

    if error:
        log.error(f"Error: {error}")
    else:
        log.debug(f"Output: {output}")
