from ._anvil_designer import _test_validatorTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..fluent import fluent, Message
from ..validators import Validator
from ..exceptions import ValidationError

class _test_validator(_test_validatorTemplate):
    TEXT_MAX_LEN = 20
    TEXT_MIN_LEN = 8

    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        fluent.configure(["de_DE"], "test_localization/{locale}/main.ftl")

        self.text_validator = Validator(
            lambda x: len(x) < self.TEXT_MAX_LEN,
            "text-too-long", max=self.TEXT_MAX_LEN
        ).chain(
            lambda x: len(x) > self.TEXT_MIN_LEN,
            "text-too-short", min=self.TEXT_MIN_LEN
        ).chain( 
            lambda x: "@" in x and not " " in x.strip(),
            "no-valid-mail"
        )

        self.text_validator_direct = Validator(
            lambda x: len(x) < self.TEXT_MAX_LEN,
            "text-too-long",
            lambda x: len(x) > self.TEXT_MIN_LEN,
            "text-too-short",
            lambda x: "@" in x and not " " in x.strip(),
            "no-valid-mail",
            max=self.TEXT_MAX_LEN,
            min=self.TEXT_MIN_LEN,
        )

        try:
            self.uneven = Validator(
                lambda x: len(x) < self.TEXT_MAX_LEN,
                "text-too-long",
                lambda x: len(x) > self.TEXT_MIN_LEN,
                "text-too-short",
                lambda x: "@" in x and not " " in x.strip(),
                max=self.TEXT_MAX_LEN,
                min=self.TEXT_MIN_LEN,
            )
            self.assertTrue(False) # Exception not raised.
        except ValueError:
            print("Exception successfully raised.")

        anvil.server.call("save_text", "My nice text.")
        print("text saved")

    def textbox_change(self, **event_args):
        self.info.text = self.text_validator(self.textbox.text, "")
        self.info.text = self.text_validator_direct(self.textbox.text, "")

    def button_1_click(self, **event_args):
        result = True
        try:
            self.text_validator.validate(self.textbox.text)
        except ValidationError as e:
            print(e)
            result = False
        if result:
            print("No exceptions")

    def server_exception_button_click(self, **event_args):
        result = False
        try:
            anvil.server.call('raise_validation_error')
            result = True
        except ValidationError as e:
            e.translate()
            print(e)


        if result:
            print("No exception raised.")




