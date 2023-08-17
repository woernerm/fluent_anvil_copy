from fluent_anvil.message import Message

class Validator:
    """Convenient validation mechanism with localized error messages."""
    
    def __init__(self, fct, msg_id: str, *args, **variables):
        """Initialize Validator.
        
        Args:
            fct: Validation function. Shall return True if validation passed. False,
                otherwise.
            msg_id: The message ID for fluent.
            variables: Keyworded parameters that are passed on to fluent.
        """
        params = [fct, msg_id, *args]
        self._message = Message(params.pop(-1), **variables)
        self._validator = params.pop(-1)

        if len(params) % 2 != 0:
            raise ValueError("The number of positional parameters must be even.")
      
        self._prior = Validator(*params, **variables) if params else None

    def _run_checks(self, value, *args, **kwargs):
        try:
            # The if-clause is necessary so that all validators in a chain
            # are run until the first one failed or all validators have been executed.
            if self._prior:
                valid, msg = self._prior._run_checks(value, *args, **kwargs)
                if not valid:
                    return False, msg
            if not self._validator.safe_parse(value, *args, **kwargs).success:
                return False, self._message
        except AttributeError:
            if not self._validator(value, *args, **kwargs):
                return False, self._message
        return True, None

    def is_valid(self, value, *args, **kwargs):
        """Validate the given value. Return True if validation passed. False, otherwise.

        Args:
            value: The value to validate.
            args: Positional arguments to pass on to the validation function.
            kwargs: Keyworded arguments to pass on to the validation function.
        """
        validity, _ = self._run_checks(value, *args, **kwargs)
        return validity
    
    def __call__(self, value, default, *args, **kwargs):
        """Validate the given value without raising an Exception. 
        
        If all validation tests pass, the default value is returned. Otherwise, the
        translated error message is returned.

        Args:
            value: The value to validate.
            default: Value to return if validation passes.
            args: Positional arguments to pass on to the validation function.
            kwargs: Keyworded arguments to pass on to the validation function.

        """  
        # Provide the current value to the translation
        self._message.variables["value"] = value
        valid, msg = self._run_checks(value, *args, **kwargs)
        if valid:
            return default
        else:
            from .fluent import fluent
            return fluent.format(msg)

    def validate(self, value, *args, **kwargs):
        """Validate the given value. Raise a ValidationError if not successful.
        
        Args:
            value: The value to validate.
            args: Positional arguments to pass on to the validation function.
            kwargs: Keyworded arguments to pass on to the validation function.
        """
        import anvil.server
        from fluent_anvil.exceptions import ValidationError
        
        self._message.variables["value"] = value
        valid, msg = self._run_checks(value, *args, **kwargs)
        if not valid:
            msg_id = msg.msg_id
            variables = {} or msg.variables
            error = ValidationError(msg_id, **variables)
            if anvil.server.context.type == "browser":
                error.translate()
            raise error
    
    def chain(self, fct, msg_id: str, **variables):
        """Append another validation criterion.
        
        Args:
            fct: Validation function. Shall return True if validation passed. False,
                Otherwise.
            msg_id: The message ID for fluent.
            variables: Keyworded parameters that are passed on to fluent.
        """
        post = Validator(
            fct=fct,
            msg_id=msg_id,
            **variables
        )
        post._prior = self
        return post
    

class LengthValidator(Validator):
    """Validates that the length of the given value is within a given range.

    This is suitable for types that the len() function can be applied to, e.g., strings,
    lists, sets, etc. The validation and __call__ dunder have an optional second parameter that
    determines whether the minimum length is enforced. This is useful if enforcing the
    minimum length depends on whether the form is about to be saved or just validated
    during filling. If it is saved, the minimum length requirement should be enforced
    (set second parameter to True). If the form is still being drafted (second parameter
    set to False) then the minimum length requirement shall only be enforced if 
    the user has already written something. If minimum length shall always be enforced,
    just omit the second parameter.
    """
    def __init__(self, minlen, maxlen, msg_too_short: str, msg_too_long: str, **variables):
        """Initialize Validator.
        
        Args:
            minlen: Minimum length of the given value. If None, the minimum length will
                not be validated and "minlen" will not be available to fluent.
            maxlen: Maximum length of the given value. If None, the maximum length will
                not be validated and "maxlen" will not be available to fluent.
            variables: Keyworded parameters that are passed on to fluent. The minlen
                and maxlen parameters are already included under the same name and
                therefore they do not have to be added manually. 
        """

        inactive = (lambda x, s = True, *a, **k: True)
        enforce_minlength = (lambda x, s = True, *a, **k: not (s or x) or len(x) >= minlen)
        enforce_maxlength = (lambda x, s = True, *a, **k: len(x) <= maxlen)
        
        super().__init__(
            inactive if minlen is None else enforce_minlength,
            msg_too_short,
            inactive if maxlen is None else enforce_maxlength,
            msg_too_long,
            **({} if minlen is None else {"minlen": minlen}),
            **({} if maxlen is None else {"maxlen": maxlen}),
            **variables
        )