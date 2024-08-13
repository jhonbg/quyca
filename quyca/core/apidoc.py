import subprocess

from core.logging import get_logger
from core.config import settings

log = get_logger(__name__)


def generate_apidoc():
    if settings.APP_ENVIRONMENT == "dev":
        return
    log.info("Generating API documentation")
    command = (
        "apidoc -i /usr/src/quyca/quyca/api/routes/v1 "
        f"-c /usr/src/quyca/quyca/core/docs/apidoc.{settings.ENVIRONMENT}.json "
        "-o /usr/src/quyca/quyca/api/apidoc "
        
    )
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()

    if error:
        log.error(f"Error: {error}")
    else:
        log.debug(f"Output: {output}")
