from ._anvil_designer import AdminPanelTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..registries import LocalSubtagRegistry

class AdminPanel(AdminPanelTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def update_registry_button_click(self, **event_args):
        task = anvil.server.call("launch_registry_update")

    def export_json_click(self, **event_args):
        local_reg = LocalSubtagRegistry()
        local_reg.download_json()
        



