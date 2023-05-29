from ._anvil_designer import NativeDatepickerTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.js
from datetime import datetime
from anvil.tz import tzlocal

class NativeDatepicker(NativeDatepickerTemplate):
    def __init__(self, **properties):
        self._min = None 
        self._max = None
        self._value = None
        self._input = None
        self._role = None
        
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self._input = anvil.js.get_dom_node(self).querySelectorAll("input")[0]

    def mkdatetime(self, value:str):
        # Anvil will stamp the timezone correctly once the datetime object is send
        # to the server. However, this ensures that the timestamp is always present.
        if not value:
            return None
        res = datetime.fromisoformat(value) if isinstance(value, str) else value
        if res.tzinfo is None or res.utcoffset() is None:
            res = res.replace(tzinfo=tzlocal())
        return res

    def inpformat(self, value):
        res = self.mkdatetime(value).replace(tzinfo=None)
        if self.pick_time:
            return res.isoformat(timespec="seconds")
        else:
            return res.date().isoformat()

    @property
    def value(self):
        return self.mkdatetime(self._input.value)

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, value):
        if self._role is not None:
            self.call_js("setRole", value)
        self._role = value

    @value.setter
    def value(self, val):
        # Ensure that the string is ISO compatible.
        self._value = self.mkdatetime(val)
        
        if self._input is not None and self._input.offsetParent is not None:
            self.call_js("setValue", self.inpformat(self._value))

    @property
    def max(self):
        if self._input is None or not self._input.max:
            return None
        self._max = self.mkdatetime(self._input.max)
        return self._max

    @max.setter
    def max(self, val):            
        # Ensure that the string is ISO compatible.
        self._max = self.mkdatetime(val)

        if self._input is not None and self._input.offsetParent is not None:            
            self._input.max = self.inpformat(self._max)

    @property
    def min(self):
        if self._input is None or not self._input.min:
            return None
        self._min = self.mkdatetime(self._input.min)
        return self._min

    @min.setter
    def min(self, val):            
        # Ensure that the string is ISO compatible.
        self._min = self.mkdatetime(val)

        if self._input is not None and self._input.offsetParent is not None:
            self._input.min = self.inpformat(self._min)

    def picker_change(self, value):
        self.raise_event("change", value=self.mkdatetime(value))

    def picker_lost_focus(self):
        self.raise_event("lost_focus")

    def picker_gain_focus(self):
        self.raise_event("focus")

    def form_show(self, **event_args):
        """This method is called when the HTML panel is shown on the screen"""        
        if self.pick_time:
            self._input.type="datetime-local"
        else:
            self._input.type="date"

        self._input.min = self.inpformat(self._min) if self._min else None
        self._input.max = self.inpformat(self._max) if self._max else None
        self.call_js("setRole", self._role)
        self.call_js("setComponent")

        if self.spacing_above and self.spacing_above != "none":
            self.call_js("setSpacingAbove", self.spacing_above)
        if self.spacing_below and self.spacing_below != "none":
            self.call_js("setSpacingBelow", self.spacing_below)
        
        if self._value:
            self.call_js("setValue", self.inpformat(self._value))
        
