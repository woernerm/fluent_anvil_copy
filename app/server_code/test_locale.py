import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from ._test import TestCase

from .locale import Locale

@anvil.server.callable
def test_locale():
    # Examples and results taken from the ponyfill package:
    # https://formatjs.io/docs/polyfills/intl-localematcher/
    print("matching locale:", Locale.match(['fr-XX', 'en'], ['fr', 'en'], 'en'))
    locale = Locale.match(['fr-XX', 'en'], ['fr', 'en'], 'en')
    TestCase.assertEqual(locale, 'fr')
    TestCase.assertEqual(locale.requested, ['fr-XX', 'en'])

    locale = Locale.match(['zh'], ['fr', 'en'], 'en')
    TestCase.assertEqual(locale, 'en')
    TestCase.assertEqual(locale.requested, ['zh'])
