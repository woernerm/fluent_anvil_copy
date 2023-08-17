from ._anvil_designer import AdminPanelTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from fluent_anvil.registries import LocalSubtagRegistry

class AdminPanel(AdminPanelTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def update_registry_button_click(self, **event_args):
        task = anvil.server.call("launch_registry_update")

    def export_language_json_click(self, **event_args):
        local_reg = LocalSubtagRegistry()
        local_reg.download_json("language")

    def export_script_json_click(self, **event_args):
        local_reg = LocalSubtagRegistry()
        local_reg.download_json("script")

    def export_region_json_click(self, **event_args):
        local_reg = LocalSubtagRegistry()
        local_reg.download_json("region")

    def export_variant_json_click(self, **event_args):
        local_reg = LocalSubtagRegistry()
        local_reg.download_json("variant")

    def export_supress_script_json_click(self, **event_args):
        local_reg = LocalSubtagRegistry()
        local_reg.download_json("suppress-script")

    def export_locale_json_click(self, **event_args):
        local_reg = LocalSubtagRegistry()
        local_reg.download_json("locale")

    def export_currency_json_click(self, **event_args):
        local_reg = LocalSubtagRegistry()
        local_reg.download_json("currency")






        



