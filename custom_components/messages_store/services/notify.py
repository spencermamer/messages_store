import logging
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
from .add_message import add_message
from .helpers import log_error

_LOGGER = logging.getLogger(__name__)

async def notify(hass: HomeAssistant, repository, call: ServiceCall) -> ServiceResponse:
    _LOGGER.debug("notify service called")
    try:
        response = await add_message(hass, repository, call)
        return response
    except Exception as e:
        return log_error("notify", e)
