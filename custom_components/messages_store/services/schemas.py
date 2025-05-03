import voluptuous as vol
from ..const import TAG_SEPARATOR_MESSAGE

def validate_no_pipe_char(value):
    if TAG_SEPARATOR_MESSAGE in value:
        raise vol.Invalid(f"The '{TAG_SEPARATOR_MESSAGE}' character is not allowed in messages.")
    return value

SLUG_SCHEMA = vol.All(vol.Match(r'^[a-zA-Z0-9_]+$'), vol.Length(min=1, max=150))
MESSAGE_SCHEMA = vol.Any(
    vol.All(str, vol.Length(min=1, max=2000), validate_no_pipe_char),  
    [vol.All(str, vol.Length(min=1, max=2000), validate_no_pipe_char)]  
)

PRIORITY_SCHEMA = vol.All(vol.Coerce(int), vol.Range(min=1, max=5))
AUDIENCE_SCHEMA = vol.Any("home", "not home", "all")
EXPIRATION_DATE_SCHEMA = vol.Any(vol.Date(), vol.Datetime())

FILTER_ITEM_SCHEMA = vol.Schema({
    vol.Required('slug'): SLUG_SCHEMA,
    vol.Optional('replace', default=[]): [vol.Any(str, int, float)],
    vol.Optional('filter', default=None): vol.Any(None, 'random')
})

ADD_EDIT_SCHEMA = vol.Schema({
    vol.Required('slug'): SLUG_SCHEMA,
    vol.Required('message'): MESSAGE_SCHEMA,
    vol.Optional('priority', default=3): PRIORITY_SCHEMA,
    vol.Optional('audience', default="all"): AUDIENCE_SCHEMA,
    vol.Optional('expiration_date'): EXPIRATION_DATE_SCHEMA,
})

DELETE_SCHEMA = vol.Schema({
    vol.Required('slug'): SLUG_SCHEMA,
})

GET_SCHEMA = vol.Schema({
    vol.Required('slug'): SLUG_SCHEMA,
    vol.Optional('replace', default=[]): [vol.Any(str, int, float)],
    vol.Optional('filter', default=None): vol.Any(None, 'random')
})

GET_MESSAGES_SCHEMA = vol.Schema({
    vol.Optional('filter', default=[]): [FILTER_ITEM_SCHEMA],
    vol.Optional('grouped', default=False): vol.Boolean(),  
    vol.Optional('force_random', default=False): vol.Boolean(), 
})

ADD_BULK_MESSAGES_SCHEMA = vol.Schema({
    vol.Required(str): vol.All(vol.Schema({
        vol.Required(vol.All(str, vol.Length(min=1, max=150))): vol.All([vol.Required(vol.Any(str, vol.Length(min=1, max=2000), validate_no_pipe_char))])
    }))
})
