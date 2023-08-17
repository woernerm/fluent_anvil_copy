from ._anvil_designer import _test_locale_matchTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..fluent import fluent, Message as M
from ..locale import Locale
from .._test import TestCase

class _test_locale_match(_test_locale_matchTemplate, TestCase):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        files = [
            "test_localization/{locale}/main.ftl",
            "test_localization/{locale}/extras.ftl"
        ]

        fluent.configure(["es_MX", "en_US"], files)

        # Examples and results taken from the ponyfill package:
        # https://formatjs.io/docs/polyfills/intl-localematcher/
        print("matching locale:", Locale.match(['fr-XX', 'en'], ['fr', 'en'], 'en'))
        locale = Locale.match(['fr-XX', 'en'], ['fr', 'en'], 'en')
        self.assertEqual(locale, 'fr')
        self.assertEqual(locale.requested, ['fr-XX', 'en'])

        locale = Locale.match(['zh'], ['fr', 'en'], 'en')
        self.assertEqual(locale, 'en')
        self.assertEqual(locale.requested, ['zh'])

        # Test the same stuff on the server
        anvil.server.call('test_locale')
