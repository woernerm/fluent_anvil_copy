from datetime import datetime, date, time
import anvil.js
from fluent_anvil.message import Message 
from fluent_anvil.registries import LocalSubtagRegistry
from fluent_anvil.locale import Locale

class Fluent:
    """Anvil interface for fluent and some convenience functions.

    The class interfaces with a JavaScript library that initializes fluent, feeds fluent
    the .ftl files matching the selected locale and provides some convenience functions
    like obtaining the user's preferred locale.

    The function most you will use most often is Fluent.format().

    Example:
        The following will initialize fluent with Mexican Spanish locale and return the
        translation stored with message id "hello". The name is given so that fluent
        may use it as a placeable. The last parameter is a list of fallback locales
        that will be iterated through if the given message id is not available
        for the "es_MX" locale::

            fluent = Fluent(
                "localization/{locale}/main.ftl", "es_MX", ["es_ES", "en_US"]
            )
            print(fluent.format("hello", name="John"))
        
    """

    STYLE_DIALECT_NARROW = ("dialect", "narrow",)
    STYLE_DIALECT_SHORT = ("dialect", "short",)
    STYLE_DIALECT_LONG = ("dialect", "long",)
    STYLE_STANDARD_NARROW = ("standard", "narrow",)
    STYLE_STANDARD_SHORT = ("standard", "short",)
    STYLE_STANDARD_LONG = ("standard", "long",)

    SUPPORTED_VALUE_TYPES = (date, datetime, time, int, float,)

    def _update_locale_class(self):
        new_value = f"{self._root}{self._index}"
        
        # Only update the locale class if the value changed. Otherwise
        # the index.lst would be loaded multiple times.
        if Locale.index_url != new_value:
            Locale.index_url = new_value
            requested = self._locale.requested
            self._locale = Locale.match(requested)
            
    def _reload(self):
        import anvil.server
        self._update_locale_class()

        if anvil.server.context.type == "server_module":
            return
        
        from fluent_anvil.js import fluent_js

        templates = [f"{self._root}{e}" for e in self._templates]
        fluent = fluent_js.init_localization(templates, self._locale)
        
        if fluent.dom_errors:
            raise Exception(fluent.dom_errors[0])
        if fluent.main_errors:
            raise Exception(fluent.main_errors[0])
        if not fluent.dom or not fluent.main:
            raise RuntimeError("Error initializing Localizer.")
        
        self._dom_localization = fluent.dom
        self._localization = fluent.main      

    def __init__(
        self,
        templates: list = "{locale}/main.ftl",
        root: str = "./_/theme/localization/",
        index: str = "index.lst",             
    ):
        """Initialize Fluent.

        Args:
            root: String path to the directory with the localization files.
            index: Path to the index.lst file inside the root directory, e.g. 
                "index.lst". The file contains the language tags of all available
                locales, e.g.
                de
                en-US
                en-GB
                fr
            templates: Template string or list of template strings to the .ftl 
                files, inside the given root directory. For example, 
                "{locale}/main.ftl". You can only use the {locale} placeholder. It will 
                contain the locale with underscore, e.g. "de_DE" instead of "de-DE",
                because Anvil does not support hyphens for directory names.
        """
        self._locale = Locale.auto()
        self._root = root if root.endswith("/") else f"{root}/"
        self._templates = [templates] if isinstance(templates, str) else templates
        self._index = index
        self._dom_localization = None
        self._localization = None
        self.datetime_options = {
            "dateStyle": "medium", 
            "timeStyle": "medium"
        }
        self.number_options = None
        self._reload()

    def configure(
            self, 
            locales: list = None,
            templates: list = None,
            root: str = None,
            index: str = None,
            datetime_options: dict = None,
            number_options: dict = None
    ):
        """Configure the translation system.

        Args:
            locales: A list of IETF language tags to set the translation system to in 
                order of preference. The most appropriate option will be chosen 
                automatically depending on which locales are actually available.
            templates: Template paths or list of template paths to the .ftl 
                files, inside the given root directory. For example, 
                "{locale}/main.ftl". You can only use the {locale} placeholder. It will 
                contain the locale with underscore, e.g. "de_DE" instead of "de-DE",
                because Anvil does not support hyphens for directory names.
            root: Path to the directory with localization files, e.g. 
                "./_/theme/localization/".
            index: Path to the index.lst file inside the root directory, e.g. 
                "index.lst". The file contains the language tags of all available
                locales, e.g.
                de
                en-US
                en-GB
                fr
            datetime_options: Defines default options to use when formatting dates using 
                the Fluent.format() method without any additional options. See 
                documentation of the Fluent.format() method for a (possibly incomplete) 
                list of options or the documentation of JavaScript's Intl.DateTimeFormat
                object (which is used internally) for a complete list of options. 
            number_options: Defines default options to use when formatting numbers using 
                the Fluent.format() method without any additional options. See 
                documentation of the Fluent.format() method for a (possibly incomplete) 
                list of options or the documentation of JavaScript's Intl.NumberFormat
                object (which is used internally) for a complete list of options.           
        """
        if root is not None:
            self._root = root if root.endswith("/") else f"{root}/"
        if templates is not None:
            self._templates = [templates] if isinstance(templates, str) else templates
        if index is not None:
            self._index = index    
        if locales is not None:
            self._locale = Locale(locales)
        if datetime_options is not None:
            self.datetime_options = datetime_options
        if number_options is not None:
            self.number_options = number_options
        
        self._update_locale_class()
        self._reload()
        
    @property
    def locale(self) -> list:
        """Returns the current locale including fallbacks in order of preference."""
        return self._locale
    
    @locale.setter
    def locale(self, value: Locale):
        """Set the current locale including fallbacks as a list.
        
        Args:
            value: The locale to set.
        """
        self._locale = Locale(value)
        self._reload()

    @property
    def templates(self):
        """Returns the templates paths for the fluent message files."""
        return self._templates
    
    @templates.setter
    def templates(self, value: list):    
        """Sets the template paths for the fluent message files.
        
        Args:
            value: The template paths to set.
        """    
        self._templates = [value] if isinstance(value, str) else value
        self._reload()

    @property
    def root(self):
        """Returns the path to the localization directory."""
        return self._root

    @root.setter
    def root(self, value: str):
        """Sets the path to the localization directory.
        
        Args:
            value: The path to set.
        """
        self._root = value if value.endswith("/") else f"{value}/"
        self._reload()

    @property
    def index(self):
        """Return the relative path to the index.lst file."""
        return self._index
    
    @index.setter
    def index(self, value: str):
        """Set the relative path to the index.lst file.
        
        Args:
            value: The relative path to the index.lst file.
        """
        self._index = value
        self._reload()

    def _translate_msg(self, messages):
        """Sends the given message instances to the javascript fluent library.
        
        Args:
            messages: The message id to translate.
        """        
        translations = self._localization.formatValues([e.tofluent() for e in messages])

        if not translations and messages:
            msgs = [str(m) for m in messages]
            raise LookupError(f"No translation into {self._locale} found for {', '.join(msgs)}.")   
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

    def _translate_value(self, value, **kwargs):
        """Translates a given numeric or date/time value.
        
        Args:
            value: The value convert into a localized format.
            kwargs: Options to pass on to the internal JavaScript Intl function.
        """
        from fluent_anvil.js import fluent_js

        if isinstance(value, list):
            return [self._translate_value(e) for e in value]
        elif isinstance(value, dict):
            return {k: self._translate_value(v) for k, v in value.items()}
        elif isinstance(value, (int, float,)):
            opts = kwargs or self.number_options
            return fluent_js.format_number(self._locale, value, opts)
        elif isinstance(value, (datetime, date,)):
            value = value.astimezone()
            opts = kwargs or self.datetime_options
            return fluent_js.format_date(self._locale, value.isoformat(), opts)
        elif isinstance(value, (time,)):
            # JavaScript does not accept time only. So assume the current day
            # and omit the date when displaying the datetime object. However, the
            # user may provide his/her own kwargs to overwrite this default setting.
            value = datetime.combine(date.today(), value).astimezone()
            opts = kwargs or {"hour": "numeric", "minute": "numeric"}
            return fluent_js.format_date(self._locale, value.isoformat(), opts)
        else:
            raise ValueError(f'Unable to format value of type "{type(value).__name__}".')    

    def format(self, message, *args, **kwargs):
        """Return a translation for the given message id / number / date and variables.

        You can use this function in multiple ways by providing:

        * A single message id (with optional keyworded variables to pass on to Fluent) 
        * An arbitrary number of Message instances.
        * A number (for displaying it in a localized format)
        * A date, time, or datetime object (for displaying it in a localized format)

        In case of a date, time, or datetime object you may also provide additional
        options as keyworded arguments (kwargs). Since JavaScript's Intl.DateTimeFormat
        functionality is used, the options are the same. You can find the complete
        documentation here:
        https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat/DateTimeFormat
        Some of these are:

        * dateStyle: "full", "long", "medium", "short" (the level of verbosity regarding 
          the date)
        * timeStyle: "full", "long", "medium", "short" (the level of verbosity regarding 
          the time)
        * hour12: True or False (whether to use 12-hour time or 24-hour-time)
        * TimeZoneName: "short", "long", "shortOffset", "longOffset", "shortGeneric", 
          "longGeneric" (the way of displaying the time zone)
        * year: "2-digit", "numeric",
        * month: "2-digit", "numeric", "narrow", "short", "long",
        * day: "2-digit", "numeric",
        * dayPeriod: "narrow", "short", "long"
        * hour: "2-digit", "numeric",
        * minute: "2-digit", "numeric",
        * second: "2-digit", "numeric",
        * fractionalSecondDigits: 1, 2, 3
        * weekday: "narrow", "short", "long"
        * era: "narrow", "short", "long"

        In case of a number, you may also provide these options as keyworded arguments 
        as well. Since JavaScript's Intl.NumberFormat functionality is used, the options 
        are the same. You can find the complete documentation here:
        https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat/NumberFormat
        Some of these are:
    
        * notation: "standard", "scientific", "engineering", "compact"
        * numberingSystem: arab", "arabext", "bali", "beng", "thai", "tibt", etc.
        * signDisplay: "auto", "always", "exceptZero", "negative", "never"
        * useGrouping: "always", "auto", false, "min2"
        * roundingMode: "ceil", "floor", "expand", "trunc", "halfCeil", "halfEven", etc.
        * currencySign: "accounting", "standard"


        Examples:
            You get the translation for a single message id like this::
                
                fl = Fluent("localization/{locale}/main.ftl", "es_MX", ["en_US"])
                print(fl.format("hello", name="John"))
                

            Alternatively, you can provide an arbitrary number of Message instances::
                
                fl = Fluent("localization/{locale}/main.ftl", "es_MX", ["en_US"])
                print(fl.format(
                    Message("hello", name="world"), 
                    Message(self.label, "text", "hello", name="John"),
                    Message("welcome", name="john")
                ))
                

            You can format a number::
                
                fl = Fluent("localization/{locale}/main.ftl", "es_MX", ["en_US"])
                print(fl.format(32000))
                

            You can format a date::
                
                fl = Fluent("localization/{locale}/main.ftl", "es_MX", ["en_US"])
                exdate = datetime.fromisoformat('2011-11-04T03:05:23')
                print(fl.format(date))
                

            You can format a date and provide additional options::
                
                fl = Fluent("localization/{locale}/main.ftl", "es_MX", ["en_US"])
                exdate = datetime.fromisoformat('2011-11-04T03:05:23')
                print(fl.format(date, dateStyle="full", timeStyle="short"))
                

        Args:
            message: message id (as string) or Message instance to return a
                translation for.
            args: An arbitrary number of additional Message instances (not message ids).
            kwargs: Keyworded variables to pass on to Fluent (only in case
                parameter message is a string).

        Returns: A translation string in case a string message id is given. If Message 
            instances are given, a list of translations in the same order.
        """
        def denyParam(param, name, msg):
            if param:
                raise ValueError(
                    f'Parameter {name} is not supported if message is of '
                    f'type "{type(msg).__name__}".'
                )
                
        # If a string is given, translate a single value.
        if isinstance(message, str):
            denyParam(args, "args", message)
            return self._localization.formatValue(message, kwargs) 
        elif isinstance(message, list):
            denyParam(args, "args", message)
            denyParam(kwargs, "kwargs", message)
            return self._translate_msg([Message(e) for e in message])            
        elif isinstance(message, dict):
            denyParam(args, "args", message)
            denyParam(kwargs, "kwargs", message)
            output = {k:v for k, v in message.items()} # The given dictionary shall not be modified => use a new variable.
            self._translate_msg([Message(output, key, value) for key, value in message.items()])
            return output
        elif isinstance(message, self.SUPPORTED_VALUE_TYPES):
            return self._translate_value(message, **kwargs)
            
        # If multiple Message instances are given as comma separated list, translate all of them.
        messages = (message,) + args
        return self._translate_msg(messages)

    def format_table(self, data, columns: list, options: dict = None, **kwargs):
        """Translate a list of dictionaries.

        This is meant for tabular data which consists of a list of dictionaries.
        The keys in these dictionaries represent the columns of the table. This 
        method will translate the columns given in the "columns" parameter. Empty
        cells in the table will be ignored.

        Args:
            data: The list of dictionaries to translate.
            columns: A list of dictionary keys, i.e., column names to translate.
                Other dictionary keys will not be touched.
            options: Dictionary with which one can provide options for value
                columns that contain numbers, dates, etc. Example::
                
                    { 
                        "My Date Column": {"dateStyle": "medium"},
                        "My Number Column": {"notation": "scientific"}
                    }

            kwargs: Optional keyworded variables to pass on to fluent (e.g., for
                placeables or selectors).
        """        
        # Extract all message ids for fluent. Use a set to remove duplicates.
        msg_ids = set()
        for line in data:
            for col in columns:
                entry = line.get(col, None)
                # Skip empty and value columns
                if entry and (isinstance(entry, str) or not isinstance(entry, self.SUPPORTED_VALUE_TYPES)):
                    msg_ids.add(line[col])
        msg_ids = list(msg_ids)

        # Translate all message ids and store the translations in a lookup table.        
        messages = self._translate_msg([Message(m, **kwargs) for m in msg_ids])
        trs = {m_id: messages[i] for i, m_id in enumerate(msg_ids)}

        def get_translated_line(line):
            def get_value(col, value):
                if col not in columns:
                    return value # column is not of interest.
                if isinstance(value, self.SUPPORTED_VALUE_TYPES):
                    opts = options.get(col, None)
                    return self._translate_value(value, **opts) # Column is a value to format
                return trs.get(value, None) # Column must be message.
            return {col: get_value(col, value) for col, value in line.items()}

        return [get_translated_line(line) for line in data]

    def _get_display_name(self, code: list, typename: str, style: tuple):
        """ Translate the given code using JavaScript.

        Args:
            codes: List of identifiers or single identifier string to translate.
            typename: The type ("language", "region", "currency") to translate.
            style: Style constant. Can be one of the following:
                STYLE_DIALECT_LONG, STYLE_DIALECT_SHORT, STYLE_DIALECT_NARROW,
                STYLE_STANDARD_LONG, STYLE_STANDARD_SHORT, STYLE_STANDARD_NARROW. 
        """            
        from fluent_anvil.js import fluent_js
        
        select = lambda n, c: n if n and n.lower() != c.lower() else None
        
        codes = [code] if isinstance(code, str) else code
        try:
            names = fluent_js.get_display_name(codes, self._locale, typename, *style)
        except anvil.js.ExternalError as err:
            if err.original_error.name.lower() == "rangeerror":
                return None
            raise err
            
        names = [select(name, code[i]) for i, name in enumerate(names)]
        return names[0] if isinstance(code, str) else names        

    def _get_options(self, displaytype:str, typename: str, style = STYLE_DIALECT_LONG, translatable_only: bool = True) -> dict:
        """Return the options for the given display type, style, etc.
        
        Args:
            displaytype: The type from which to get the name to display, e.g., 
                "language", "region", "script".
            typename: The type ("language", "region", "currency") to translate.
            style: Style constant. Can be one of the following:
                STYLE_DIALECT_LONG, STYLE_DIALECT_SHORT, STYLE_DIALECT_NARROW,
                STYLE_STANDARD_LONG, STYLE_STANDARD_SHORT, STYLE_STANDARD_NARROW. 
            translatable_only: If True, skip options that cannot be adequately
                translated. Set to False to return all options even if the name is
                only available in English.
        """
        registry = LocalSubtagRegistry(True).get_tags(typename)
        tags = list(registry.keys()) if isinstance(registry, dict) else registry
        transl = self._get_display_name(tags, displaytype, style)
        if not translatable_only:
            # Find entries that were not translated and use the default english fallback.
            transl = [transl[i] if transl[i] else registry[t] for i, t in enumerate(tags)]
            return {tags[i]: trs for i, trs in enumerate(transl)}
        return {tags[i]: trs for i, trs in enumerate(transl) if trs}

    def get_locale_name(self, locale, style = STYLE_DIALECT_LONG):
        """Returns the translated name of the given locale(s).

        The name of the given locale is returned in the language fluent has
        been configured for.

        Args:
            locale: The locale or list of locales to get the translated name for.
            style: Style constant. Can be one of the following:
                STYLE_DIALECT_LONG, STYLE_DIALECT_SHORT, STYLE_DIALECT_NARROW,
                STYLE_STANDARD_LONG, STYLE_STANDARD_SHORT, STYLE_STANDARD_NARROW. 
        """
        return self._get_display_name(Locale.clean(locale), "language", style)

    def get_region_name(self, code, style = STYLE_DIALECT_LONG):
        """Returns the translated name of the given regions(s).

        The name of the given region code is returned in the language fluent has
        been configured for.

        Args:
            code: The region code (e.g., "AT", "US", "GB", etc.) or list of 
                region codes to get the translated name for.
            style: Style constant. Can be one of the following:
                STYLE_DIALECT_LONG, STYLE_DIALECT_SHORT, STYLE_DIALECT_NARROW,
                STYLE_STANDARD_LONG, STYLE_STANDARD_SHORT, STYLE_STANDARD_NARROW. 
        """
        cd = code.upper() if isinstance(code, str) else [e.upper() for e in code]
        return self._get_display_name(cd, "region", style)

    def get_currency_name(self, code, style = STYLE_DIALECT_LONG):
        """Returns the translated name of the given currency / currencies.

        The name of the given currency code (e.g., "USD", "EUR") is returned in 
        the language fluent has been configured for.

        Args:
            code: The currency code (e.g., "USD", "EUR", "CNY", etc.) or list of 
                currency codes to get the translated name for.
            style: Style constant. Can be one of the following:
                STYLE_DIALECT_LONG, STYLE_DIALECT_SHORT, STYLE_DIALECT_NARROW,
                STYLE_STANDARD_LONG, STYLE_STANDARD_SHORT, STYLE_STANDARD_NARROW. 
        """
        return self._get_display_name(code, "currency", style)

    def get_script_name(self, code, style = STYLE_DIALECT_LONG):
        """Returns the translated name of the given script(s).

        The name of the given script code is returned in the language fluent has
        been configured for.

        Args:
            code: The script code (e.g., "Arab", "Latn", etc.) or list of 
                script codes to get the translated name for.
            style: Style constant. Can be one of the following:
                STYLE_DIALECT_LONG, STYLE_DIALECT_SHORT, STYLE_DIALECT_NARROW,
                STYLE_STANDARD_LONG, STYLE_STANDARD_SHORT, STYLE_STANDARD_NARROW. 
        """
        cd = code.capitalize() if isinstance(code, str) else [e.capitalize() for e in code]
        return self._get_display_name(cd, "script", style) 

    def get_region_options(self, style = STYLE_DIALECT_LONG, translatable_only: bool = False) -> dict:
        """Return all region tags and their translated name for display.
        
        Args:
            style: Style constant. Can be one of the following:
                STYLE_DIALECT_LONG, STYLE_DIALECT_SHORT, STYLE_DIALECT_NARROW,
                STYLE_STANDARD_LONG, STYLE_STANDARD_SHORT, STYLE_STANDARD_NARROW. 
            translatable_only: If True, skip options that cannot be adequately
                translated. Set to False to return all options even if the name is
                only available in English.
        """
        return self._get_options("region", "region", style, translatable_only)

    def get_language_options(self, style = STYLE_DIALECT_LONG, translatable_only: bool = False) -> dict:
        """Return all language tags and their translated name for display.
        
        Args:
            style: Style constant. Can be one of the following:
                STYLE_DIALECT_LONG, STYLE_DIALECT_SHORT, STYLE_DIALECT_NARROW,
                STYLE_STANDARD_LONG, STYLE_STANDARD_SHORT, STYLE_STANDARD_NARROW. 
            translatable_only: If True, skip options that cannot be adequately
                translated. Set to False to return all options even if the name is
                only available in English.
        """
        return self._get_options("language", "language", style, translatable_only)

    def get_script_options(self, style = STYLE_DIALECT_LONG, translatable_only: bool = False) -> dict:
        """Return all script tags and their translated name for display.
        
        Args:
            style: Style constant. Can be one of the following:
                STYLE_DIALECT_LONG, STYLE_DIALECT_SHORT, STYLE_DIALECT_NARROW,
                STYLE_STANDARD_LONG, STYLE_STANDARD_SHORT, STYLE_STANDARD_NARROW. 
            translatable_only: If True, skip options that cannot be adequately
                translated. Set to False to return all options even if the name is
                only available in English.
        """
        return self._get_options("script", "script", style, translatable_only)

    def get_locale_options(self, style = STYLE_DIALECT_LONG, translatable_only: bool = False) -> dict:
        """Return complete locale tags (e.g., en-US) and their translated name.
        
        Args:
            style: Style constant. Can be one of the following:
                STYLE_DIALECT_LONG, STYLE_DIALECT_SHORT, STYLE_DIALECT_NARROW,
                STYLE_STANDARD_LONG, STYLE_STANDARD_SHORT, STYLE_STANDARD_NARROW. 
            translatable_only: If True, skip options that cannot be adequately
                translated. Set to False to return all options even if the name is
                only available in English.
        """
        return self._get_options("language", "locale", style, translatable_only)

    def get_currency_options(self, style = STYLE_DIALECT_LONG, translatable_only: bool = False) -> dict:
        """Return all currencies and their translated name for display.
        
        Args:
            style: Style constant. Can be one of the following:
                STYLE_DIALECT_LONG, STYLE_DIALECT_SHORT, STYLE_DIALECT_NARROW,
                STYLE_STANDARD_LONG, STYLE_STANDARD_SHORT, STYLE_STANDARD_NARROW. 
            translatable_only: If True, skip options that cannot be adequately
                translated. Set to False to return all options even if the name is
                only available in English.
        """
        return self._get_options("currency", "currency", style, translatable_only)

try:
    import anvil.server
    fluent = Fluent()
except (TypeError, ImportError) as e:
    try:
        if __sphinx_build__:
            from unittest.mock import Mock
            fluent = Mock()
    except NameError:
        raise e