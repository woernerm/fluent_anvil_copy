from anvil.tables import app_tables
from fluent_anvil.locale import Locale
from fluent_anvil.validators import Validator


class Text(dict):
    """This class models a static text for which there are multiple translations.
    
    The primary use case of this class is best explained using an example: Imagine
    you are a German speaker living in Germany. Your first language is German and most
    of your colleagues at work speak German but a few of your colleagues only speak
    English. You want to write some technical text. You can explain it best in German,
    but you also want your English-speaking colleagues to understand it. Fortunately,
    the system you write your text in allows you to enter your text in multiple
    languages. This is where this class comes into play: It manages multiple
    translations of the same static text. 
    
    If you apply str(my_text_object) on your text, it will also automatically select the 
    language the user prefers. You can also transmit the Text object between client
    and server because it is a portable class. You can save some bandwidth by
    using the slice() method before transmission so that only one or a small number
    of translations is transmitted.
    """
    
    def __init__(self, data: dict, validator: Validator = None):
        """Initialize the Text object.
        
        Args:
            data: Dictionary with texts in different languages. The dictionary key
                must be an IETF language tag and the value the corresponding text for
                that language.
            validator: The validator to use. See fluent_anvil.validators. You can also set
                it later using the Text.validator attribute.
        """
        # Is the data wrapped in a type / value dictionary?
        if "type" in data and "value" in data:
            data = data["value"]
            
        self.clear()
        self.update({Locale.clean(k): v for k, v in data.items()})
        self._locale = str(Locale.select(self.keys()))
        self.validator = validator

    def slice(self, locales, count=1):
        """Create a Text with a subset of available locales.
        
        This is used to save bandwidth during transmission by omitting locales that are
        not needed at the client. One simply provides a list of preferred locales, and
        the slice will be created using the `count` best matching locales.

        Args:
            locales: The preferred locales to use.
            count: The number of locales to include in the slice.
        """
        if locales is None:
            return Text({k:v for k,v in self.items()}, self.validator)
        if not locales:
            raise ValueError(
                "Cannot create text translation slice without any given locales."
            )
        selected = Locale.match(locales, self.keys(), count=count)
        txt = Text({k:v for k,v in self.items() if k in selected}, self.validator)
        txt._locale = str(selected)
        return txt

    @property
    def locales(self):
        """Return the available locales."""
        return list(self.keys())

    def get(self, locale, default=None):
        return super().get(Locale.clean(locale), default)

    def __getitem__(self, locale):
        return super().__getitem__(Locale.clean(locale))

    def __setitem__(self, locale, value):
        super().__setitem__(Locale.clean(locale), value)

    def __contains__(self, locale):
        return super().__contains__(Locale.clean(locale))

    def __serialize__(self, global_data):
        return {k:v for k,v in self.items()}

    def __deserialize__(self, data, global_data):
        self.__init__(data)

    def validate(self, *args, **kwargs):
        """Validate the Text object. Raise a ValidationError if not successful.
        
        Args:
            args: Positional arguments to pass on to the validation function.
            kwargs: Keyworded arguments to pass on to the validation function.
        """
        if not self.validator:
            raise TypeError("No validator was given to perform validation.")
            
        for locale, text in self.items():
            self.validator.validate(text, *args, locale=locale, **kwargs)

    def is_valid(self, *args, **kwargs):
        """Validate the given text. Return True if validation passed. False, otherwise.

        Args:
            args: Positional arguments to pass on to the validation function.
            kwargs: Keyworded arguments to pass on to the validation function.
        """
        if not self.validator:
            raise TypeError("No validator was given to perform validation.")
            
        for locale, text in self.items():
            if not self.validator.is_valid(text, *args, locale=locale, **kwargs):
                return False
        return True            

    def __str__(self):        
        return self[self._locale]

try:
    from anvil.server import portable_class
    Text = portable_class(Text)
except ImportError:
    pass


