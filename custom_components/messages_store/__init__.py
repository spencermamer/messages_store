import logging
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, SupportsResponse
from .view import async_setup_view
from .services.helpers import log_error
from .const import DOMAIN, DB_FILENAME
from .services import (
    add_notice,
    get_notice,
    get_notices,
    edit_notice,
    delete_notice,
    add_bulk_notices,
    # create_notice_from_notification, # Removed
    acknowledge_notice 
)
from .services.schemas import (
    ADD_EDIT_SCHEMA,
    GET_SCHEMA,
    GET_NOTICES_SCHEMA,
    DELETE_SCHEMA,
    ADD_BULK_NOTICES_SCHEMA,
    ACKNOWLEDGE_NOTICE_SCHEMA # Added
)
from .repository.sqlite_notices_store_repository import SQLiteNoticeStoreRepository

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    _LOGGER.debug("async_setup_entry called")
    try:
        await async_setup_view(hass)
        return await setup_services(hass, entry)
    except Exception as e:
        return log_error("Setting up Notices Store", e)

async def setup_services(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    try:
        """Helper function to set up services."""

        db_path = hass.config.path(DB_FILENAME)
        repository = SQLiteNoticeStoreRepository(db_path)
        
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}
        hass.data[DOMAIN]['repository'] = repository # Storing repository

        await hass.async_add_executor_job(repository.create_table)

        def wrap_service(service_func):
            async def wrapped_service(call):
                # The repository is now fetched from hass.data within the service call if needed,
                # or passed if the service function signature still expects it.
                # For existing services, they might still expect 'repository' as a direct arg.
                # For the new notify platform, it will fetch from hass.data.
                return await service_func(hass, repository, call)
            return wrapped_service

        hass.services.async_register(
            DOMAIN,
            'add_notice',
            wrap_service(add_notice),
            schema=ADD_EDIT_SCHEMA,
            supports_response=SupportsResponse.ONLY
        )

        hass.services.async_register(
            DOMAIN,
            'get_notice',
            wrap_service(get_notice),
            schema=GET_SCHEMA,
            supports_response=SupportsResponse.ONLY
        )

        hass.services.async_register(
            DOMAIN,
            'get_notices',
            wrap_service(get_notices),
            schema=GET_NOTICES_SCHEMA,
            supports_response=SupportsResponse.ONLY
        )

        hass.services.async_register(
            DOMAIN,
            'edit_notice',
            wrap_service(edit_notice),
            schema=ADD_EDIT_SCHEMA,
            supports_response=SupportsResponse.ONLY
        )

        hass.services.async_register(
            DOMAIN,
            'delete_notice',
            wrap_service(delete_notice),
            schema=DELETE_SCHEMA,
            supports_response=SupportsResponse.ONLY
        )

        hass.services.async_register(
            DOMAIN,
            'add_bulk_notices',
            wrap_service(add_bulk_notices),
            schema=ADD_BULK_NOTICES_SCHEMA,
            supports_response=SupportsResponse.ONLY
        )

        # Removing create_notice_from_notification service registration
        # hass.services.async_register(
        #     DOMAIN,
        #     'create_notice_from_notification', 
        #     wrap_service(create_notice_from_notification), 
        #     schema=ADD_EDIT_SCHEMA, 
        #     supports_response=SupportsResponse.ONLY
        # )

        hass.services.async_register(
            DOMAIN,
            'acknowledge_notice',
            wrap_service(acknowledge_notice),
            schema=ACKNOWLEDGE_NOTICE_SCHEMA,
            supports_response=SupportsResponse.ONLY
        )

        entry.async_on_unload(entry.add_update_listener(update_listener))

        return True
    
    except Exception as e:
        return log_error("Setting up Notices Store", e)

async def update_listener(hass: HomeAssistant, config_entry: config_entries.ConfigEntry):
    """Handle options update."""
    _LOGGER.debug("Config entry updated, reloading services...")

    await setup_services(hass, config_entry)


async def async_unload_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    """Unload Messages Store config entry."""
    services = [
        "add_notice",
        "get_notice",
        "get_notices",
        "edit_notice",
        "delete_notice",
        "add_bulk_notices",
        "acknowledge_notice",
    ]

    for service in services:
        if hass.services.has_service(DOMAIN, service):
            hass.services.async_remove(DOMAIN, service)

    try:
        from homeassistant.components.frontend import async_remove_panel

        async_remove_panel(hass, "messages_store", warn_if_unknown=False)
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Failed removing panel: %s", err)

    hass.data.pop(DOMAIN, None)
    return True
