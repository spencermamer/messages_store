import random
import logging
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
from .helpers import log_error
from ..repository import MessagesStore
from .tag_replacer import replace_all

_LOGGER = logging.getLogger(__name__)

async def get_message(hass: HomeAssistant, repository: MessagesStore, call: ServiceCall) -> ServiceResponse:
    _LOGGER.debug("get_message service called")
    try:
        slug = call.data.get('slug')
        replace_list = call.data.get('replace', [])
        filter_option = call.data.get('filter', None)

        message = repository.retrieve_message(slug)

        if message:
            message_list = replace_all(hass, repository, message, slug, replace_list)

            print(message_list)

            if filter_option == "random":
                message_list = [random.choice(message_list)]

            return {"status": True, "message": message_list}
        else:
            return {"status": False, "message": "No message found for slug"}

    except Exception as e:
        return log_error("get_message", e)
