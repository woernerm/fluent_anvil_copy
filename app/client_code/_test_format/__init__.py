from ._anvil_designer import _test_formatTemplate
from anvil import *
from ..fluent import fluent, Message as M

from datetime import timedelta


class _test_format(_test_formatTemplate):
    def __init__(self, **properties):
        self.label.text = "hello"
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        print(type(fluent))

        print("Preferred:", fluent.get_preferred_locales())
        print("Preferred:", fluent.get_preferred_locales("en_US"))

        fluent.configure(["es_MX", "en_US"], "test_localization/{locale}/main.ftl")
        
        print(fluent.format("hello"))
        print(fluent.format("hello", name="John"))
        print(fluent.format("time-elapsed", duration=12342423.234 ))

        fluent.set_locale("en_US")

        print(fluent.format(
            M("hello", name="world"), 
            M("hello", name="world"), 
            M("welcome", name="john")
        ))

        fluent.set_locale(["en_US"])

        translations = fluent.format(["hello", "welcome"])
        print("List of string translations: ", translations)

        translations = fluent.format({
            "my key 1": "hello",
            "my key 2": "welcome"
        })
        print("dictionary of translations: ", translations)

        fluent.format(
            M(self.label, "text", "hello", name="John"),
            M(self.text, "placeholder", "hello", name="John")
        )

        print(fluent.js.dom_localization)
        print(fluent.js.localization)

        fluent_hyphen = fluent.configure(["en-US", "es-MX"], "test_localization/{locale}/main.ftl")
        print("hyphen: ", fluent.format("hello"))
        print("hyphen: ", fluent.format("hello", name="John"))





    
