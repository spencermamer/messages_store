import random
import re
from ..const import TAG_SEPARATOR_MESSAGE

def replace_slugs(message, slug, repository):
    slug_pattern = re.compile(r'\(slug:(.+?)\)')
    processed_slugs = set()

    def replace(match):

        slug_name = match.group(1)
        if slug_name == slug or slug_name in processed_slugs:
            return match.group(0)
        
        replacement_message = repository.retrieve_message(slug_name)
        if replacement_message and not slug_pattern.search(replacement_message):
            replacement_list = [msg.strip() for msg in replacement_message.split(TAG_SEPARATOR_MESSAGE)]
            return random.choice(replacement_list) if len(replacement_list) > 1 else replacement_list[0]
        else:
            return match.group(0)

    return slug_pattern.sub(replace, message)

def replace_states(message, hass):
    state_pattern = re.compile(r'\(state:(.+?)(\((.*?)\))?\)')

    def replace(match):
        entity_id = match.group(1)
        filters = match.group(3)  

        state = hass.states.get(entity_id)

        if state:
            try:
                state_value = float(state.state)
                is_numeric = True
            except ValueError:
                state_value = state.state
                is_numeric = False

            unit = state.attributes.get('unit_of_measurement', '')

            if filters:
                filters = [f.strip() for f in filters.split(',')]

                if is_numeric:
                    round_filter = [f for f in filters if f.startswith('round')]
                    if round_filter:
                        if round_filter[0] == 'round':
                            state_value = f"{round(state_value)}"
                        else:
                            decimals = int(round_filter[0].replace('round', ''))
                            state_value = f"{round(state_value, decimals)}"

                if 'unit' in filters and unit:
                    state_value = f"{state_value} {unit}"

            return str(state_value)

        return match.group(0)

    return state_pattern.sub(replace, message)


def replace_placeholders(message_list, replace_list):
    for i in range(len(message_list)):
        for value in replace_list:
            message_list[i] = message_list[i].replace('%s', str(value), 1)
    return message_list

def replace_all(hass, repository, message, slug, replace_list):
    message = replace_slugs(message, slug, repository)
    message = replace_states(message, hass)
    
    message_list = [msg.strip() for msg in message.split(TAG_SEPARATOR_MESSAGE)]

    message_list = replace_placeholders(message_list, replace_list)

    return message_list
