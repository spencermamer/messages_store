import random
import logging
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
from .helpers import log_error
from ..repository import NoticesStore
from .tag_replacer import replace_all

_LOGGER = logging.getLogger(__name__)

async def get_notice(hass: HomeAssistant, repository: NoticesStore, call: ServiceCall) -> ServiceResponse:
    _LOGGER.debug("get_notice service called")
    try:
        slug = call.data.get('slug')
        replace_list = call.data.get('replace', [])
        filter_option = call.data.get('filter', None)

        notice_content = repository.retrieve_notice(slug)

        if notice_content:
            notice_list = replace_all(hass, repository, notice_content, slug, replace_list)

            print(notice_list)

            if filter_option == "random":
                notice_list = [random.choice(notice_list)]

            return {"status": True, "notice": notice_list}
        else:
            return {"status": False, "message": "No notice found for slug"}

    except Exception as e:
        return log_error("get_notice", e)
