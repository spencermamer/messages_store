import voluptuous as vol

SLUG_SCHEMA = vol.All(vol.Match(r'^[a-zA-Z0-9_]+$'), vol.Length(min=1, max=150))
MESSAGE_SCHEMA = vol.Any(
    vol.All(str, vol.Length(min=1, max=2000)),  # Validação de tamanho para string
    [vol.All(str, vol.Length(min=1, max=2000))]  # Validação de tamanho para lista de strings
)

FILTER_ITEM_SCHEMA = vol.Schema({
    vol.Required('slug'): SLUG_SCHEMA,
    vol.Optional('replace', default=[]): [vol.Any(str, int, float)],
    vol.Optional('filter', default=None): vol.Any(None, 'random')
})

ADD_EDIT_SCHEMA = vol.Schema({
    vol.Required('slug'): SLUG_SCHEMA,
    vol.Required('message'): MESSAGE_SCHEMA,
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
    vol.Optional('filter', default=[]): [FILTER_ITEM_SCHEMA]
})

ADD_BULK_MESSAGES_SCHEMA = vol.Schema({
    vol.Required(str): vol.All(vol.Schema({
        vol.Required(vol.All(str, vol.Length(min=1, max=150))): vol.All([vol.Required(vol.Any(str, vol.Length(min=1, max=2000)))])
    }))
})