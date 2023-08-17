from ._anvil_designer import _test_textTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .._test import TestCase

from ..text import Text

class _test_text(_test_textTemplate, TestCase):  
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        txt = Text({
            "de-DE": "Das ist ein schöner Text.",
            "en-US": "This is a nice Text.",
            "it": "Questo è un bellissimo testo."
        })

        print(txt["de-DE"])
        print(txt["en_US"])
        self.assertEqual(txt["de-DE"], "Das ist ein schöner Text.")
        self.assertEqual(txt["de_DE"], "Das ist ein schöner Text.")
        self.assertEqual(txt["en-US"], "This is a nice Text.")
        self.assertEqual(txt["en_US"], "This is a nice Text.")
        self.assertEqual(txt["it"], "Questo è un bellissimo testo.")

        self.assertEqual(txt.get("de-DE"), "Das ist ein schöner Text.")
        self.assertEqual(txt.get("de_DE"), "Das ist ein schöner Text.")
        self.assertEqual(txt.get("en-US"), "This is a nice Text.")
        self.assertEqual(txt.get("en_US"), "This is a nice Text.")
        self.assertEqual(txt.get("it"), "Questo è un bellissimo testo.")

        self.assertTrue("de-DE" in txt)
        self.assertTrue("de_DE" in txt)
        self.assertTrue("en-US" in txt)
        self.assertTrue("en_US" in txt)
        self.assertTrue("it" in txt)
        self.assertFalse("fr" in txt)
        self.assertFalse("de-AT" in txt)
        self.assertFalse("de_AT" in txt)

        server_txt = anvil.server.call("test_get_full_text", None)
        print(server_txt["de-DE"])
        print(server_txt["en_US"])
        self.assertEqual(server_txt["de-DE"], "Das ist ein schöner Text.")
        self.assertEqual(server_txt["de_DE"], "Das ist ein schöner Text.")
        self.assertEqual(server_txt["en-US"], "This is a nice Text.")
        self.assertEqual(server_txt["en_US"], "This is a nice Text.")
        self.assertEqual(server_txt["it"], "Questo è un bellissimo testo.")

        self.assertEqual(server_txt.get("de-DE"), "Das ist ein schöner Text.")
        self.assertEqual(server_txt.get("de_DE"), "Das ist ein schöner Text.")
        self.assertEqual(server_txt.get("en-US"), "This is a nice Text.")
        self.assertEqual(server_txt.get("en_US"), "This is a nice Text.")
        self.assertEqual(server_txt.get("it"), "Questo è un bellissimo testo.")

        self.assertEqual(sorted(["de-DE", "en-US", "it"]), sorted(server_txt.locales))
        self.assertTrue("de-DE" in server_txt)
        self.assertTrue("de_DE" in server_txt)
        self.assertTrue("en-US" in server_txt)
        self.assertTrue("en_US" in server_txt)
        self.assertTrue("it" in server_txt)
        self.assertFalse("fr" in server_txt)
        self.assertFalse("de-AT" in server_txt)
        self.assertFalse("de_AT" in server_txt)

        incomplete_txt = anvil.server.call("test_get_full_text", ["de-DE", "en_US"])
        self.assertEqual(sorted(["de-DE"]), sorted(incomplete_txt.locales))
        self.assertTrue("de-DE" in incomplete_txt)
        self.assertTrue("de_DE" in incomplete_txt)
        self.assertFalse("en-US" in incomplete_txt)
        self.assertFalse("en_US" in incomplete_txt)
        self.assertFalse("it" in incomplete_txt)
        self.assertFalse("fr" in incomplete_txt)
        self.assertFalse("de-AT" in incomplete_txt)
        self.assertFalse("de_AT" in incomplete_txt)

        incomplete_txt = anvil.server.call("test_get_full_text", ["en_US", "de-DE"])
        self.assertEqual(sorted(["en-US"]), sorted(incomplete_txt.locales))
        self.assertFalse("de-DE" in incomplete_txt)
        self.assertFalse("de_DE" in incomplete_txt)
        self.assertTrue("en-US" in incomplete_txt)
        self.assertTrue("en_US" in incomplete_txt)
        self.assertFalse("it" in incomplete_txt)
        self.assertFalse("fr" in incomplete_txt)
        self.assertFalse("de-AT" in incomplete_txt)
        self.assertFalse("de_AT" in incomplete_txt)

        returned_txt = anvil.server.call('test_return_text', txt)
        self.assertEqual(sorted(["de-DE", "en-US", "it"]), sorted(returned_txt.locales))
        self.assertTrue("de-DE" in returned_txt)
        self.assertTrue("de_DE" in returned_txt)
        self.assertTrue("en-US" in returned_txt)
        self.assertTrue("en_US" in returned_txt)
        self.assertTrue("it" in returned_txt)
        self.assertFalse("fr" in returned_txt)
        self.assertFalse("de-AT" in returned_txt)
        self.assertFalse("de_AT" in returned_txt)

        txt = Text({
            "de-DE": "Das ist ein schöner Text.",
            "en-US": "This is a nice Text.",
            "it": "Questo è un bellissimo testo."
        })

        slice = txt.slice(["en-US"])
        self.assertEqual(str(slice), "This is a nice Text.")
        slice = txt.slice(["de-DE"])
        self.assertEqual(str(slice), "Das ist ein schöner Text.")
        print(txt)
        slice = txt.slice(["de_DE"])
        self.assertEqual(str(slice), "Das ist ein schöner Text.")
        slice = txt.slice(["en-US"])
        self.assertEqual(str(slice), "This is a nice Text.")
        print(txt)
        slice = txt.slice(["en_US"])
        self.assertEqual(str(slice), "This is a nice Text.")
        slice = txt.slice(["it"])
        self.assertEqual(str(slice), "Questo è un bellissimo testo.")
        
