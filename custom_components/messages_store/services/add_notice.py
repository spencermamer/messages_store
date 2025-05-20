import logging
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
from .helpers import log_error
from ..repository import NoticesStore
from ..const import TAG_SEPARATOR_MESSAGE

_LOGGER = logging.getLogger(__name__)

async def add_notice(hass: HomeAssistant, repository: NoticesStore, call: ServiceCall) -> ServiceResponse:
    _LOGGER.debug("add_notice service called")
    try:
        slug = call.data.get('slug')
        notice_content = call.data.get('notice') # Renamed from message to notice_content to avoid conflict with status message
        priority = call.data.get('priority', 3)
        audience = call.data.get('audience', 'all')
        expiration_date = call.data.get('expiration_date')

        if isinstance(notice_content, list):
            notice_content = f"{TAG_SEPARATOR_MESSAGE} ".join(notice_content)

        if await hass.async_add_executor_job(repository.slug_exists, slug):
            return {"status": False, "message": f"Slug '{slug}' already exists"}

        await hass.async_add_executor_job(repository.insert_notice, slug, notice_content, priority, audience, expiration_date)
        return {"status": True, "message": f"Notice added with slug {slug}"}

    except Exception as e:
        return log_error("add_notice", e)
