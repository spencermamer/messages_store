import random
import logging
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
from .helpers import log_error
from .tag_replacer import replace_all  
from ..repository import NoticesStore
from ..const import TAG_SEPARATOR_MESSAGE

_LOGGER = logging.getLogger(__name__)

async def get_notices(hass: HomeAssistant, repository: NoticesStore, call: ServiceCall) -> ServiceResponse:
    try:
        _LOGGER.debug("get_notices service called")
        filter_list = call.data.get('filter', [])
        grouped = call.data.get('grouped', False)
        force_random = call.data.get('force_random', False)  

        def retrieve_filtered_notices():
            results = {} if grouped else []
            for filter_item in filter_list:
                slug = filter_item['slug']
                replace_list = filter_item.get('replace', [])
                filter_option = filter_item.get('filter', None)

                notice_content = repository.retrieve_notice(slug)

                if notice_content:
                    notice_list = replace_all(hass, repository, notice_content, slug, replace_list)

                    if filter_option == "random" or force_random:
                        notice_list = [random.choice(notice_list)]

                    if grouped:
                        results[slug] = notice_list[0] if filter_option == "random" or force_random else notice_list
                    else:
                        results.append({
                            "slug": slug,
                            "notice": notice_list[0] if filter_option == "random" or force_random else notice_list
                        })
            return results

        def retrieve_all_notices():
            all_results = repository.retrieve_all_notices()
            if grouped:
                formatted_results = {}
                for entry in all_results:
                    slug = entry['slug']
                    notice_list = [msg.strip() for msg in entry['notice'].split(TAG_SEPARATOR_MESSAGE)]
                    if force_random:
                        notice_list = random.choice(notice_list)
                    formatted_results[slug] = notice_list
                return formatted_results
            else:
                formatted_results = []
                for entry in all_results:
                    slug = entry['slug']
                    notice_list = [msg.strip() for msg in entry['notice'].split(TAG_SEPARATOR_MESSAGE)]
                    if force_random:
                        notice_list = [random.choice(notice_list)]
                    formatted_results.append({
                        "slug": slug,
                        "notice": notice_list
                    })
                return formatted_results

        if filter_list:
            data = await hass.async_add_executor_job(retrieve_filtered_notices)
        else:
            data = await hass.async_add_executor_job(retrieve_all_notices)

        if data:
            return {"status": True, "data": data}
        else:
            return {"status": False, "message": "No notices found"}

    except Exception as e:
        return log_error("get_notices", e)
