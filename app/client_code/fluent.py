import anvil.js
from fluent_anvil.message import Message 


class __Fluent:
    """Anvil interface for fluent and some convenience functions.

    The class interfaces with a JavaScript library that initializes fluent, feeds fluent
    the .ftl files matching the selected locale and provides some convenience functions
    like obtaining the user's preferred locale.

    The function most you will use most often is Fluent.format().

    Example:
        ``
        fluent = Fluent("localization/{locale}/main.ftl", "es_MX", ["es_ES", "en_US"])
        print(fluent.format("hello", name="John"))
        ``
        This will initialize fluent with Mexican Spanish locale and return the
        translation stored with message id "hello". The name is given so that fluent
        may use it as a placeable. The last parameter is a list of fallback locales
        that will be iterated through if the given message id is not available
        for the "es_MX" locale.
    """

    class __JSInterface:
        """The JavaScript library that is used to interface with fluent creates a
        "DOMLocalization" and a "Localization" object. You can access it directly
        using the public Fluent.js attribute.

        Example:
            ``
            fl = Fluent("localization/{locale}/main.ftl", "es_MX", ["es_ES", "en_US"])
            print(fl.js.formatValue("hello", { name: "John"}))
            ``
            This will call the original fluent-dom API.
        """

        ASSET_URL = "./_/theme/"
        FLUENT_LIB = "fluent_anvil.js"

        def __init__(
            self,
            path_template: str,
            locale: str,
            fallback_locales: list = None,
            path_prefix: str = None,
        ):
            """Initialize Fluent's DOMLocalization and Localization object."""
            
            # Determine the path prefix and ensure it ends with a forward slash.
            prefix = self.ASSET_URL if path_prefix is None else path_prefix
            prefix = "" if path_template.startswith(prefix) else prefix
            prefix = prefix if prefix.endswith("/") else f"{prefix}/"

            self.module = anvil.js.import_from(f"{self.ASSET_URL}{self.FLUENT_LIB}")
            fluent = self.module.init_localization(
                f"{prefix}{path_template}", locale, fallback_locales
            )
            
            if fluent.dom_errors:
                raise Exception(fluent.dom_errors[0])

            if fluent.main_errors:
                raise Exception(fluent.main_errors[0])

            if not fluent.dom or not fluent.main:
                raise RuntimeError("Error initializing Localizer.")

            self.dom_localization = fluent.dom
            self.localization = fluent.main

    @classmethod
    def _clean_locale(cls, locale: str):
        """Ensure valid IETF language tags.

        Since Anvil does not support hyphens for directories, users may use an 
        underscore for the locale names as well. However, this would not be valid IETF 
        language tags. Therefore, replace any underscores with hyphens. The JavaScript 
        library will switch to underscore again when loading the assets.
        """
        return locale.replace("_", "-")

    def __init__(
        self,
        locales: list,
        path_template: str,
        path_prefix: str = None,
    ):
        """Initialize Fluent.

        Args:
            locales: List of locale names in the order of decreasing preference. Can be 
                written with both hyphen or underscore, e.g. both "en_US" and "en-US" 
                will work. The first given locale is the most preferred one while the
                remaining locales will be used as fallback in case a translation cannot
                be determined for the most preferred locale.
            path_template: Template string to the .ftl files, e.g.
                "localization/{locale}/main.ftl". You can only use the {locale}
                placeholder. It will contain the locale with underscore, e.g. "de_DE"
                instead of "de-DE", because Anvil does not support hyphens for
                directory names.
            path_prefix: Prefix for the given path. Will be "./_/theme/" if not given.
                The prefix will be prepended to path_template if not already present.
                This is meant as a convenience for novice users and reduce typing
                effort.
        """
        self.configure(locales, path_template, path_prefix)

    def set_locale(self, locales: list):
        """Sets a new locale to translate to.

        Args:
            locale: List of locale names in the order of decreasing preference. Can be 
            written with both hyphen or underscore, e.g. both "en_US" and "en-US" will 
            work.      
        """
        
        self.configure(locales, self._path_template, self._path_prefix)

    def configure(
            self, 
            locales: list,
            path_template: str,
            path_prefix: str = None,
    ):
        """Sets a all basic configuration options.

        Args:
            locales: List of locale names in the order of decreasing preference. Can be 
                written with both hyphen or underscore, e.g. both "en_US" and "en-US" 
                will work. The first given locale is the most preferred one while the
                remaining locales will be used as fallback in case a translation cannot
                be determined for the most preferred locale.
            path_template: Template string to the .ftl files, e.g.
                "localization/{locale}/main.ftl". You can only use the {locale}
                placeholder. It will contain the locale with underscore, e.g. "de_DE"
                instead of "de-DE", because Anvil does not support hyphens for
                directory names.
            path_prefix: Prefix for the given path. Will be "./_/theme/" if not given.
                The prefix will be prepended to path_template if not already present.
                This is meant as a convenience for novice users and reduce typing
                effort.
                  
        """
        self._path_template = path_template
        self._path_prefix = path_prefix
        
        if not locales:
            self._locales = None
            self.js = None
        else:
            self._locales = [locales] if isinstance(locales, str) else locales
            self._locales = [self._clean_locale(e) for e in self._locales]
    
            self.js = self.__JSInterface(
                self._path_template, 
                self._locales[0], 
                self._locales[1:] if len(self._locales) > 1 else [], 
                self._path_prefix
            )

    @classmethod
    def get_preferred_locales(cls, fallback: str = None) -> list:
        """Return the user's preferred locales.
        
        Uses the Get-User-Locale library https://github.com/wojtekmaj/get-user-locale .

        Args:
            fallback: The fallback locale to return if operation fails.

        Returns:
            A list of preferred locales (most preferrable first).
        """
        module_js = anvil.js.import_from(
            f"{cls.__JSInterface.ASSET_URL}{cls.__JSInterface.FLUENT_LIB}"
        )
        fallback = cls._clean_locale(fallback) if fallback else None
        locales = module_js.get_user_locales(fallback)
        return locales if isinstance(locales, list) else [locales]

    def _translate(self, messages):
        """Sends the given message instances to the javascript fluent library."""

        if not self.js:
            raise RuntimeError("Fluent is not configured, yet.")

        translations = self.js.localization.formatValues([e.tofluent() for e in messages])

        if not translations and messages:
            msgs = [str(m) for m in messages]
            raise LookupError(f"No translation found for {', '.join(msgs)}.")   
        elif len(translations) != len(messages):
            raise LookupError("At least one translation failed.")    

        # Set the translation of the output object, if specified.
        for i, msg in enumerate(messages):
            # Since there is JavaScript behind this Python code, some list entries may be
            # unspecified. Finding these requires a trick: Accessing the variable will fail
            # if the element is unspecified, because Python will think that the variable has been
            # referenced before assignment. This causes an UnboundLocalError which can be caught.
            try:
                trs = translations[i]
                if not trs:
                    trs = None                
            except (UnboundLocalError, KeyError):
                raise LookupError(f"No translation found for {msg}.")           
            
            if msg.obj is None:
                continue
            try:
                msg.obj[msg.attribute] = trs
            except TypeError:
                setattr(msg.obj, msg.attribute, trs)

        return translations if len(messages) > 1 else translations[0]

    def format(self, message, *args, **kwargs):
        """Return a translation for the given message id and variables.

        You can either provide a single message id (with optional keyworded variables
        to pass on to Fluent) or an arbitrary number of Message instances.

        Examples:
            You get the translation for a single message id like this:
            ``
            fl = Fluent("localization/{locale}/main.ftl", "es_MX", ["en_US"])
            print(fl.format("hello", name="John"))
            ``

            Alternatively, you can provide an arbitrary number of Message instances:
            ``
            fl = Fluent("localization/{locale}/main.ftl", "es_MX", ["en_US"])
            print(fl.format(
                Message("hello", name="world"), 
                Message(self.label, "text", "hello", name="John"),
                Message("welcome", name="john")
            ))
            ``

        Args:
            message: message id (as string) or Message instance to return a
                translation for.
            args: An arbitrary number of additional Message instances (not message ids).
            kwargs: Keyworded variables to pass on to Fluent (only in case
                parameter message is a string).

        Returns: A translation string in case a string message id is given. If Message 
            instances are given, a list of translations in the same order.
        """

        if not self.js:
            raise RuntimeError("Fluent is not configured, yet.")

        # If a string is given, translate a single value.
        if isinstance(message, str):
            if args:
                raise ValueError(
                    "Parameter args is not supported if message is a string."
                )
            return self.js.localization.formatValue(message, kwargs)

        if kwargs:
            raise ValueError(
                "Parameter kwargs is only supported if message is a string"
            )            
            
        if isinstance(message, list):
            if args:
                raise ValueError(
                    "Parameter args is not supported if message is a list."
                )
            return self._translate([Message(e) for e in message])            
        elif isinstance(message, dict):
            if args:
                raise ValueError(
                    "Parameter args is not supported if message is a dictionary."
                )
            output = {k:v for k, v in message.items()} # The given dictionary shall not be modified => use a new variable.
            self._translate([Message(output, key, value) for key, value in message.items()])
            return output
            
        # If multiple Message instances are given as comma separated list, translate all of them.
        messages = (message,) + args
        return self._translate(messages)

    def format_table(self, data, columns: list, **kwargs):
        """Translate a list of dictionaries.

        This is meant for tabular data which consists of a list of dictionaries.
        The keys in these dictionaries represent the columns of the table. This 
        method will translate the columns given in the "columns" parameter. Empty
        cells in the table will be ignored.

        Args:
            data: The list of dictionaries to translate.
            columns: A list of dictionary keys, i.e. column names to translate.
                Other dictionary keys will not be touched.
            kwargs: Optional keyworded variables to pass on to fluent (e.g. for
                placeables or selectors).
        """        
        # Extract all message ids for fluent. Use a set to remove duplicates.
        msg_ids = set()
        for line in data:
            for col in columns:
                entry = line.get(col, None)
                if entry: # Skip empty columns
                    msg_ids.add(line[col])
        msg_ids = list(msg_ids)

        # Translate all message ids and store the translations in a lookup table.
        messages = self._translate([Message(m, **kwargs) for m in msg_ids])
        trs = {m_id: messages[i] for i, m_id in enumerate(msg_ids)}

        def get_translated_line(line):
            get_value = lambda c, v: trs.get(v, None) if c in columns else v
            return {col: get_value(col, value) for col, value in line.items()}

        return [get_translated_line(line) for line in data]
    

fluent = __Fluent(None, "localization/{locale}/main.ftl")