import logging
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
from .helpers import log_error
from ..repository import NoticesStore

_LOGGER = logging.getLogger(__name__)

async def delete_notice(hass: HomeAssistant, repository: NoticesStore, call: ServiceCall) -> ServiceResponse:
    _LOGGER.debug("delete_notice service called")
    try:
        slug = call.data.get('slug')

        deleted = await hass.async_add_executor_job(repository.delete_notice, slug)

        if deleted:
            return {"status": True, "message": f"Notice deleted for slug {slug}"}
        else:
            return {"status": False, "message": f"No notice found for slug {slug}"}

    except Exception as e:
        return log_error("delete_notice", e)
