from ._anvil_designer import _test_localizedmultiselectdropdownTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime

class _test_localizedmultiselectdropdown(_test_localizedmultiselectdropdownTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        options = [
            {
                "key": "My first option", 
                "value": 1
            },
            {
                "key": "My second option", 
                "value": 2,
                "subtext": "pick me",
                "tokens": "Manhours"
            }
        ]
        self.dropdown.items = options

    def native_datepicker_1_change(self, value, **event_args):
        """This method is called Called when the value is modified."""
        print(value, type(value))

    def form_show(self, **event_args):
        """This method is called when the HTML panel is shown on the screen"""
        self.native_datepicker_1.value = datetime.now()

    def content_panel_show(self, **event_args):
        """This method is called when the column panel is shown on the screen"""
        pass

    def native_datepicker_1_lost_focus(self, **event_args):
        """This method is called when the datepicker loses focus"""
        print("lost focus")

    def native_datepicker_1_focus(self, **event_args):
        """This method is called when the datepicker gets focus"""
        print("got focus")





