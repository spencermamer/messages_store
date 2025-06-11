import json
import os

DOMAIN = "messages_store"
NAME = "Messages Store"
PANEL_URL = "/messages-store-files/app.js"
DB_FILENAME = "messages_store.db"
TAG_SEPARATOR_MESSAGE = "|"

COMPONENT_PATH = os.path.dirname(os.path.realpath(__file__))

MANIFEST = json.load(
        open( os.path.join( COMPONENT_PATH, 'manifest.json') )
    )
    
VERSION = MANIFEST['version']
