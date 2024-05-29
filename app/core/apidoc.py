import subprocess

from core.logging import get_logger
from core.config import settings

log = get_logger(__name__)


def generate_apidoc():
    if settings.ENVIRONMENT == "dev":
        return
    log.info("Generating API documentation")
    command = (
        "apidoc -i /usr/src/app/app/api/routes/v1 "
        f"-c /usr/src/app/app/core/docs/apidoc.{settings.ENVIRONMENT}.json "
        "-o /usr/src/app/app/api/apidoc "
        
    )
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()

    if error:
        log.error(f"Error: {error}")
    else:
        log.debug(f"Output: {output}")
