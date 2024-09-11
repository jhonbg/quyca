import subprocess
from os import getenv

from core.logging import get_logger

log = get_logger(__name__)


def generate_apidoc():
    log.info("Generating API documentation")
    command = (
        "apidoc -i /quyca/routes "
        f"-c /quyca/core/docs/apidoc.{getenv('ENVIRONMENT', 'dev')}.json "
        "-o /quyca/core/docs/apidoc"
    )
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()

    if error:
        log.error(f"Error: {error}")
    else:
        log.debug(f"Output: {output}")
