import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .text import Text
from ._test import TestCase

@anvil.server.callable
def test_get_full_text(requested_locales: list):
    txt = Text({
        "de-DE": "Das ist ein schöner Text.",
        "en-US": "This is a nice Text.",
        "it": "Questo è un bellissimo testo."
    })
    return txt.slice(requested_locales)

@anvil.server.callable
def test_return_text(mytext: Text):
    TestCase.assertEqual(mytext['en-US'], "This is a nice Text.")
    TestCase.assertEqual(mytext['it'], "Questo è un bellissimo testo.")
    TestCase.assertEqual(mytext['de-DE'], "Das ist ein schöner Text.")

    return mytext
    