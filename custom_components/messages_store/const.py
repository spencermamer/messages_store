import json, os

DOMAIN = "messages_store"
NAME = "Messages Store"
PANEL_URL = "/messages-store-files/app.js"
PATH_DB_SQLITE = "home-assistant_v2.db"
TAG_SEPARATOR_MESSAGE = "|"

COMPONENT_PATH = os.path.dirname(os.path.realpath(__file__))

MANIFEST = json.load(
        open( os.path.join( COMPONENT_PATH, 'manifest.json') )
    )
    
VERSION = MANIFEST['version']
