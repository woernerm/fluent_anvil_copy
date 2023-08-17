from ._anvil_designer import _test_formatTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..fluent import fluent, Message as M
from ..locale import Locale

import datetime
from .._test import TestCase


class _test_format(_test_formatTemplate, TestCase):
    def __init__(self, **properties):
        self.label.text = "hello"
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        print(type(fluent))

        fluent.root = "./_/theme/test_localization/"

        print("Preferred:", Locale.preferred())
        print("Preferred:", Locale.preferred("en_US"))

        fluent.templates = [
            "{locale}/main.ftl",
            "{locale}/extras.ftl"
        ]
        fluent.locale = Locale(["es_MX", "en_US"])
        self.assertEqual(fluent.locale, ["es-MX", "en-US"])
        
        
        self.assertEqual(fluent.format("hello", name="John").strip(), "Hola ⁨John⁩.")
        self.assertEqual(fluent.format("my-unique-translation"), "My fantastic translation.")
        self.assertEqual(
            fluent.format("time-elapsed", duration=12342423.234).strip(), 
            "Time-elapsed: ⁨12,342,423.234⁩s."
        )

        fluent.locale = Locale("en_US")

        self.assertEqual(fluent.format(
            M("hello", name="world"), 
            M("hello", name="world"), 
            M("welcome", name="john")
        ), ['Hello!', 'Hello!', '"Welcome!"'])

        fluent.locale = Locale(["en_US"])
        self.assertEqual(fluent.format(["hello", "welcome"]), ['Hello!', '"Welcome!"'])

        self.assertEqual(fluent.format({
            "my key 1": "hello",
            "my key 2": "welcome"
        }),  {'my key 1': 'Hello!', 'my key 2': '"Welcome!"'})

        fluent.locale = Locale(["es_MX", "en_US"])
        fluent.format(
            M(self.label, "text", "hello", name="John"),
            M(self.text, "placeholder", "hello", name="John")
        )
        self.assertEqual(self.label.text, "Hola ⁨John⁩.")
        self.assertEqual(self.text.placeholder, "Hola ⁨John⁩.")

        fluent.locale = Locale(["en-US", "es-MX"])
        fluent.templates = "{locale}/main.ftl"
        self.assertEqual(fluent.format("hello"), "Hello!")
        self.assertEqual(fluent.format("hello", name="John"), "Hello!")

        exdate = datetime.datetime.fromisoformat('2011-11-04T03:05:23')
        self.assertEqual(fluent.format(320000), "320,000")
        fluent.locale = Locale(["de_DE"])
        self.assertEqual(fluent.format(320000), "320.000")
        
        fluent.locale = ["en_US"]
        self.assertEqual(fluent.format(exdate), "Nov 4, 2011, 3:05:23 AM")
        fluent.locale = ["de_DE"]
        self.assertEqual(fluent.format(exdate), "04.11.2011, 03:05:23")

        extime = datetime.time.fromisoformat('04:23:01')
        fluent.locale = Locale(["en_US"])
        self.assertEqual(fluent.format(extime), "4:23 AM")
        fluent.locale = Locale(["de_DE"])
        self.assertEqual(fluent.format(extime), "04:23")

        fluent.locale = Locale(["en-US"])
        # Test format_table
        data = [
            {"title": "my title", "key": "hello", "date": exdate, "number": 64000},
            {"title": "my title", "key": "hello", "date": exdate, "number": 432},
            {"title": "my title", "key": "welcome", "date": exdate, "number": 12800000}
        ]
        self.assertEqual(
            fluent.format_table(
                data, 
                ["key", "date", "number"], 
                {
                    "date": {"dateStyle": "full"},
                    "number": {"notation": "scientific", "signDisplay": "always"}
                }
            ),
            [{'title': 'my title', 'key': 'Hello!', 'date': 'Friday, November 4, 2011', 'number': '+6.4E4'}, 
             {'title': 'my title', 'key': 'Hello!', 'date': 'Friday, November 4, 2011', 'number': '+4.32E2'}, 
             {'title': 'my title', 'key': '"Welcome!"', 'date': 'Friday, November 4, 2011', 'number': '+1.28E7'}
            ]
        )

        fluent.configure(
            datetime_options = {
                "dateStyle": "full", 
                "timeStyle": "full",
            },
            number_options = {
                "notation": "scientific",
                "signDisplay": "always"
            }
        )




    
