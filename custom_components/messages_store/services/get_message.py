import random
import logging
import re
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
from .helpers import log_error
from ..repository import MessagesStore

_LOGGER = logging.getLogger(__name__)

async def get_message(hass: HomeAssistant, repository: MessagesStore, call: ServiceCall) -> ServiceResponse:
    _LOGGER.debug("get_message service called")
    try:
        slug = call.data.get('slug')
        replace_list = call.data.get('replace', [])
        filter_option = call.data.get('filter', None)

        message = repository.retrieve_message(slug)

        if message:
            slug_pattern = re.compile(r'\(slug:(.+?)\)')
            state_pattern = re.compile(r'\(state:(.+?)\)')
            processed_slugs = set()

            def replace_slugs(match):
                slug_name = match.group(1)
                if slug_name == slug or slug_name in processed_slugs:
                    return match.group(0)
                
                replacement_message = repository.retrieve_message(slug_name)
                
                if replacement_message and not slug_pattern.search(replacement_message):
                    replacement_list = [msg.strip() for msg in replacement_message.split(',')]
                    return random.choice(replacement_list) if len(replacement_list) > 1 else replacement_list[0]
                else:
                    return match.group(0)

            def replace_states(match):
                entity_id = match.group(1)
                state = hass.states.get(entity_id)
                if state:
                    return f"{state.state} {state.attributes.get('unit_of_measurement', '')}".strip()
                return match.group(0)

            message = slug_pattern.sub(replace_slugs, message)
            message = state_pattern.sub(replace_states, message)

            message_list = [msg.strip() for msg in message.split(',')]

            if filter_option == "random":
                message_list = [random.choice(message_list)]

            for i in range(len(message_list)):
                for value in replace_list:
                    message_list[i] = message_list[i].replace('%s', str(value), 1)

            return {"status": True, "message": message_list}
        else:
            return {"status": False, "message": "No message found for slug"}

    except Exception as e:
        return log_error("get_message", e)
