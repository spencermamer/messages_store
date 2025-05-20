import logging
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
from .helpers import log_error
from ..repository import NoticesStore
from ..const import TAG_SEPARATOR_MESSAGE

_LOGGER = logging.getLogger(__name__)

async def edit_notice(hass: HomeAssistant, repository: NoticesStore, call: ServiceCall) -> ServiceResponse:
    _LOGGER.debug("edit_notice service called")
    try:
        slug = call.data.get('slug')
        new_notice = call.data.get('notice')
        priority = call.data.get('priority')
        audience = call.data.get('audience')
        expiration_date = call.data.get('expiration_date')

        if isinstance(new_notice, list):
            new_notice = f"{TAG_SEPARATOR_MESSAGE} ".join(new_notice)

        # Note: repository.update_notice was already updated in a previous step to accept these kwargs
        updated = await hass.async_add_executor_job(
            repository.update_notice, 
            slug, 
            notice=new_notice, 
            priority=priority, 
            audience=audience, 
            expiration_date=expiration_date
        )

        if updated:
            return {"status": True, "message": f"Notice updated for slug {slug}"}
        else:
            return {"status": False, "message": f"No notice found for slug {slug}"}

    except Exception as e:
        return log_error("edit_notice", e)
