import logging
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
from .helpers import log_error
from ..repository import MessagesStore

_LOGGER = logging.getLogger(__name__)

async def delete_message(hass: HomeAssistant, repository: MessagesStore, call: ServiceCall) -> ServiceResponse:
    _LOGGER.debug("delete_message service called")
    try:
        slug = call.data.get('slug')

        deleted = await hass.async_add_executor_job(repository.delete_message, slug)

        if deleted:
            return {"status": True, "message": f"Message deleted for slug {slug}"}
        else:
            return {"status": False, "message": f"No message found for slug {slug}"}

    except Exception as e:
        return log_error("delete_message", e)
