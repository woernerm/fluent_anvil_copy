import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from json import loads
from anvil.http import request

JSON_DB_URL = anvil.server.get_app_origin() + "/_/theme/fluent_subtag_registry.json"

@anvil.server.callable
def fluent_jsondb_get(**kwargs):
    response = request(JSON_DB_URL)
    cont = loads(response.get_bytes().decode("utf-8"))
    return next((row for row in cont if all(row.get(ck) == cv for ck, cv in kwargs.items())))

@anvil.server.callable
def fluent_jsondb_search(**kwargs):
    response = request(JSON_DB_URL)
    cont = loads(response.get_bytes().decode("utf-8"))
    return [row for row in cont if all(row.get(ck) == cv for ck, cv in kwargs.items())]
    
