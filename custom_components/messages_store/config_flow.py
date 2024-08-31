import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, NAME

class MessagesStoreConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Messages Store."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(
            title=NAME,
            data={},  
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MessagesStoreOptionsFlowHandler(config_entry)

class MessagesStoreOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Messages Store options."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return self.async_create_entry(
            title="",
            data={},  
        )
