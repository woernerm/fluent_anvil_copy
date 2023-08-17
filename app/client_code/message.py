import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Message:
    """Container for a translation request.

    The Message class is used to define a translation request. You can define a
    message id and optional keyworded variables that are passed to fluent (e.g., for
    placeables). Alternatively, you may use it in a way similar to Python's setattr()
    function: In addition to the afore mentioned parameters you can define an object
    and the name of the attribute to write to. The translated string will then be
    assigned to that attribute automatically.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the Message class.

        Examples:
            Variant 1:
                ``Message(my_label, "text", "my_message_identifier", name="John")``
                This example assumes that you have a form containing the label my_label
                for greeting the user. The greeting message is defined
                in the .ftl file using identifier my_message_identifier, for example:
                ``my_message_identifier = Welcome, { $name }!`` 
                or
                ``my_message_identifier = Willkommen, { $name }!``
                In the example above, the name is given as keyworded argument.
            Varian 2:
                ``Message("my_message_identifier", name="John")``
                Same as above without assigning the translation.

        Args:
            args: You may provide object (any), attribute name (str) and message id
                (str). Alternatively, you can provide the message id (str) only.
            kwargs: Optional keyworded variables to pass on to fluent (e.g., for
                placeables or selectors).
        """
        try:
            # Assume the user wants to assign the translation to an object attribute.
            self.obj, self.attribute, self.msg_id = args
            self.variables = kwargs
        except ValueError:
            msg = args[0]
            if isinstance(msg, type(self)):
                # In case the given argument is already a message, use the same values.
                self.obj = msg.obj
                self.attribute = msg.attribute
                self.msg_id = msg.msg_id
                self.variables = msg.variables
            else:
                # Assume the user wants to obtain the translated string only.
                self.obj = None
                self.attribute = None
                self.msg_id = args[0]
                self.variables = kwargs

    def tofluent(self):
        """Generate parameters for the Javascript fluent library."""
        return {"id": self.msg_id, "args": self.variables}

    def __serialize__(self, global_data):
        return {
            "msg_id": self.msg_id,
            "variables": self.variables
        }

    def __deserialize__(self, data, global_data):
        self.__init__(
            data["msg_id"],
            data.get("variabels", {})
        )
    
    def __str__(self):
        return f"<Message {self.msg_id}>"

    def __repr__(self):
        return f"<Message {self.msg_id}>"
    
try:
    from anvil.server import portable_class
    Message = portable_class(Message)
except ImportError:
    pass