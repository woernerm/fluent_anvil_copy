import anvil.server
from fluent_anvil.lib import LengthValidator

text_length_validator = LengthValidator(
    3, 200,
    "text-too-short",
    "text-too-long",
    my_context_var = "my context"
)

@anvil.server.callable
def save_text(text):
    text_length_validator.validate(text, True)
    # Do the actual saving here  

@anvil.server.callable
def raise_validation_error():
    from fluent_anvil.lib import ValidationError
    raise ValidationError("no-valid-mail", value="my_value")
