import anvil.server
from json import dumps, loads, JSONDecodeError

class ValidationError(anvil.server.AnvilWrappedError):
    """Exception to represent a validation error.
    
    The class inherits from AnvilWrappedError and is registered with anvil
    so that the exception can be thrown both on client and server side. The only
    difference is that the translate() method has to be called when catching errors
    from server side, because translation can only be done at the client.

    Implementation detail: Many attempts have been performed to define simple member 
    variables for the fluent message id and the corresponding variables that shall 
    be used in the translation. However, the values have all been removed somwhere 
    between the client and the server. Therefore, the data is encoded to json first 
    and stored as exception message.
    """

    def __init__(self, message_id: str, **kwargs):
        data = {
            "msg_id": message_id,
            "variables": kwargs
        }
        super().__init__(dumps(data))
        self.translation = None   

    def _get_args(self):
        try:
            data = loads(super().__str__())
        except JSONDecodeError:
            data = loads(self.message)
        return data.get("msg_id", None), data.get("variables", {})

    def translate(self):
        if self.translation:
            return # Already done
        if not anvil.server.context.type == "browser":
            raise RuntimeError("Can only translate in browser environment.")
        from fluent_anvil.lib import fluent
        msg_id, variables = self._get_args()
        self.translation = fluent.format(msg_id, **variables)

    def __str__(self):
        msg_id, variables = self._get_args()
        if self.translation:
            return f'{type(self).__name__}: {self.translation}'.strip()
        return f'{type(self).__name__}: {msg_id}'.strip()

class NoSubtagRegistry(Exception):
    pass

class NotFound(Exception):
    pass

anvil.server._register_exception_type('fluent_anvil.exceptions.ValidationError', ValidationError)