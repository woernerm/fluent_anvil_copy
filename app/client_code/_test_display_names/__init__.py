from ._anvil_designer import _test_display_namesTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..fluent import fluent, Message as M
from ..registries import CLDRFile, CLDRLocale
from .._test import TestCase

from datetime import timedelta


class _test_display_names(_test_display_namesTemplate, TestCase):
    def __init__(self, **properties):
        self.label.text = "hello"
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        fluent.configure(["de-DE"], "test_localization/{locale}/main.ftl")
        print(fluent.get_currency_name("ISK"))

        self.assertEqual(fluent.get_locale_name("de-DE", fluent.STYLE_STANDARD_LONG), "Deutsch (Deutschland)")
        self.assertEqual(fluent.get_locale_name("de-AT", fluent.STYLE_STANDARD_LONG), "Deutsch (Österreich)")
        self.assertEqual(fluent.get_locale_name("de-AT", fluent.STYLE_DIALECT_LONG), "Österreichisches Deutsch")
        self.assertEqual(fluent.get_locale_name(["de-DE"], fluent.STYLE_DIALECT_LONG), ["Deutsch (Deutschland)"])
        print(fluent.get_locale_name("de-AT", fluent.STYLE_STANDARD_LONG))
        
        self.assertEqual(fluent.get_currency_name("eur"), "Euro")
        self.assertEqual(fluent.get_currency_name("CNY"), "Renminbi Yuan")

        self.assertEqual(fluent.get_region_name("US"), "Vereinigte Staaten")
        self.assertEqual(fluent.get_region_name("AT"), "Österreich")

        self.assertEqual(fluent.get_script_name("Latn"), "Lateinisch")
        print(fluent.get_script_name("Latn"))

        # Incorrect subtags shall lead to None
        self.assertEqual(fluent.get_script_name("adrab"), None)
        self.assertEqual(fluent.get_region_name("adrab"), None)
        self.assertEqual(fluent.get_currency_name("adrab"), None)
        self.assertEqual(fluent.get_locale_name("adrab"), None)

        self.assertLess(
            len(fluent.get_locale_options(translatable_only = True)),
            len(fluent.get_locale_options(translatable_only = False))
        )
