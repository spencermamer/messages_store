import logging
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
from ..repository import NoticesStore
from .helpers import log_error

_LOGGER = logging.getLogger(__name__)

async def acknowledge_notice(hass: HomeAssistant, repository: NoticesStore, call: ServiceCall) -> ServiceResponse:
    _LOGGER.debug("acknowledge_notice service called")
    try:
        slug = call.data.get('slug')
        acknowledged_bool = call.data.get('acknowledged')

        if slug is None or acknowledged_bool is None:
            return {"status": False, "message": "Slug and acknowledged status are required."}

        acknowledged_int = 1 if acknowledged_bool else 0
        
        success = await hass.async_add_executor_job(
            repository.set_acknowledged_status, slug, acknowledged_int
        )

        if success:
            return {"status": True, "message": f"Notice '{slug}' acknowledgement status updated to {acknowledged_bool}."}
        else:
            return {"status": False, "message": f"Failed to update notice '{slug}' acknowledgement status. Notice not found or status unchanged."}

    except Exception as e:
        return log_error("acknowledge_notice", e)
