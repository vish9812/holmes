import logging.config

from app.utils import constants
from app.utils.settings import settings

logging.basicConfig(
    level=logging.getLevelName(settings.HOLMES_LOG_LEVEL),
    format="%(levelname)s|%(asctime)s|%(module)s|%(funcName)s|%(lineno)d|%(message)s",
)

app_logger = logging.getLogger(constants.APP_NAME)
