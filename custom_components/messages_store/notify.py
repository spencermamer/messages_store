import logging
import uuid
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
import homeassistant.components.notify as notify_service

from ..const import DOMAIN
from ..repository import NoticesStore # Using ABC for type hint


_LOGGER = logging.getLogger(__name__)

async def async_get_service(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> notify_service.BaseNotificationService | None:
    """Get the Notices Store notification service."""
    # Check if the repository instance is stored in hass.data
    if DOMAIN not in hass.data or "repository" not in hass.data[DOMAIN]:
        _LOGGER.error(
            "Notices Store repository not found in hass.data. "
            "Ensure it's set up in async_setup_entry."
        )
        return None
    
    repository = hass.data[DOMAIN]["repository"]
    return NoticesNotificationService(hass, repository)


class NoticesNotificationService(notify_service.BaseNotificationService):
    """Implementation of a notification service for the Notices Store."""

    def __init__(self, hass: HomeAssistant, repository: NoticesStore) -> None:
        """Initialize the service."""
        self.hass = hass # Store hass instance
        self._repository = repository

    @property
    def targets(self) -> dict[str, str] | None:
        """Return a dictionary of supported targets."""
        # This service does not use targets in the traditional sense,
        # as it's saving to a central store.
        return None

    async def async_send_message(self, message: str, **kwargs: Any) -> None:
        """Send a message (save as a notice)."""
        title = kwargs.get("title")
        data = kwargs.get("data", {})

        slug = data.get("slug")
        if not slug and title:
            slug = title.lower().replace(" ", "_").replace("-", "_") + "_" + uuid.uuid4().hex[:6]
            # Basic sanitization for slug from title
            slug = "".join(c if c.isalnum() or c == "_" else "_" for c in slug)
            slug = slug.strip("_") 
        elif not slug:
            slug = "notice_" + uuid.uuid4().hex[:8]

        priority = data.get("priority", 3)
        audience = data.get("audience", "all")
        expiration_date = data.get("expiration_date")
        
        # If 'notice_content_list' is in data, it could be used to create a multi-line notice
        # For now, 'message' is the primary content.
        # If a list is provided in 'message' via YAML, HA might pass it as a string.
        # The service call schema for add_notice handles a list or string.
        # Here, 'message' from notify.send_message is typically a string.
        notice_content_to_save = message

        try:
            if await self.hass.async_add_executor_job(self._repository.slug_exists, slug):
                _LOGGER.warning(
                    f"Slug '{slug}' already exists. Notification not added via notify platform. "
                    "Consider providing a unique slug in data."
                )
                # Optionally, could update, or append a new unique part to slug here.
                return

            await self.hass.async_add_executor_job(
                self._repository.insert_notice,
                slug,
                notice_content_to_save,
                priority,
                audience,
                expiration_date,
                # acknowledged defaults to 0 in the repository's insert_notice method
            )
            _LOGGER.info(f"Notice '{slug}' added via notify platform.")
        except Exception as e:
            _LOGGER.error(f"Error adding notice '{slug}' via notify platform: {e}")
