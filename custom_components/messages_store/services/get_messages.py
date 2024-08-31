import random
import re
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
from .helpers import log_error
from ..repository import MessagesStore

async def get_messages(hass: HomeAssistant, repository: MessagesStore, call: ServiceCall) -> ServiceResponse:
    try:
        filter_list = call.data.get('filter', [])

        def replace_slugs_in_message(message, slug, processed_slugs=None):
            if processed_slugs is None:
                processed_slugs = set()

            slug_pattern = re.compile(r'\(slug:(.+?)\)')
            state_pattern = re.compile(r'\(state:(.+?)\)')

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

            return message

        def retrieve_filtered_messages():
            results = []
            for filter_item in filter_list:
                slug = filter_item['slug']
                replace_list = filter_item.get('replace', [])
                filter_option = filter_item.get('filter', None)

                message = repository.retrieve_message(slug)

                if message:
                    message = replace_slugs_in_message(message, slug)
                    message_list = [msg.strip() for msg in message.split(',')]

                    if filter_option == "random":
                        message_list = [random.choice(message_list)]

                    for i in range(len(message_list)):
                        for value in replace_list:
                            message_list[i] = message_list[i].replace('%s', str(value), 1)

                    results.append({
                        "slug": slug,
                        "message": message_list
                    })
            return results

        if filter_list:
            data = await hass.async_add_executor_job(retrieve_filtered_messages)
        else:
            def retrieve_all_messages():
                all_results = repository.retrieve_all_messages()
                formatted_results = []
                for entry in all_results:
                    slug = entry['slug']
                    message_list = [msg.strip() for msg in entry['message'].split(',')]
                    formatted_results.append({
                        "slug": slug,
                        "message": message_list
                    })
                return formatted_results

            data = await hass.async_add_executor_job(retrieve_all_messages)

        if data:
            return {"status": True, "data": data}
        else:
            return {"status": False, "message": "No messages found"}

    except Exception as e:
        return log_error("get_messages", e)
