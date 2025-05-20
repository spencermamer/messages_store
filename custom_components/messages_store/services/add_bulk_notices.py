import re
import logging
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
from .helpers import log_error
from ..repository import NoticesStore
from ..const import TAG_SEPARATOR_MESSAGE

_LOGGER = logging.getLogger(__name__)

async def add_bulk_notices(hass: HomeAssistant, repository: NoticesStore, call: ServiceCall) -> ServiceResponse:
    _LOGGER.debug("add_bulk_notices service called")
    try:
        data = call.data.get("data", {})
        
        invalid_slugs = []
        existing_slugs = []
        inserted_slugs = []

        slug_pattern = re.compile(r'^[a-zA-Z0-9_]+$')

        for slug, notices_data in data.items():
            if not slug_pattern.match(slug):
                invalid_slugs.append(slug)
                continue

            if await hass.async_add_executor_job(repository.slug_exists, slug):
                existing_slugs.append(slug)
                continue

            if isinstance(notices_data, list):
                notice = f"{TAG_SEPARATOR_MESSAGE} ".join(notices_data)  
            else:
                notice = str(notices_data)

            await hass.async_add_executor_job(repository.insert_notice, slug, notice)
            inserted_slugs.append(slug)

        if invalid_slugs:
            return {"status": False, "message": f"Invalid slugs: {', '.join(invalid_slugs)}"}

        if existing_slugs:
            return {"status": False, "message": f"Slugs already exist: {', '.join(existing_slugs)}"}

        return {"status": True, "message": f"Successfully inserted slugs: {', '.join(inserted_slugs)}"}

    except Exception as e:
        return log_error("add_bulk_notices", e)
