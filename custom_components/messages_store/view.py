from .const import VERSION, NAME, PANEL_URL 
from homeassistant.core import HomeAssistant
from homeassistant.components.frontend import async_register_built_in_panel
from .utils import async_register_static_path

async def async_setup_view(hass: HomeAssistant):

    await async_register_static_path(
        hass,
        PANEL_URL,
        hass.config.path("custom_components/messages_store/app.js"),
        False
    )

    async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title=NAME,
        sidebar_icon="mdi:message-text",
        frontend_url_path="messages_store",
        require_admin=True,
        config={
            "_panel_custom": {
                "name": "messages-store",
                "module_url": f"{PANEL_URL}?{VERSION}",
                "embed_iframe": True
            },
            "version": VERSION
        },
    )
    