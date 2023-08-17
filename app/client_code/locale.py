from anvil.http import HttpError

class Locale(list):
    """Models a locale and its fallbacks.
    
    The Locale class is a list. As such it can contain one primary locale at index 0 and
    multiple fallback locales at the following indices.    
    """

    index_url = "./_/theme/localization/index.lst"
    """The default URL to the index.lst file that contains all available locales.
    
    The value will be modified automatically whenever fluent instance is reconfigured.
    """

    fallback = "en"
    """The default fallback locale to use if no other locale is found.
    
    The value will be modified automatically whenever fluent instance is reconfigured.
    """

    max_distance = 100
    """Maximum matching distance between requested locale and available locales."""

    def __init__(self, locale: str = None):
        if not locale:
            super().__init__([])
        elif isinstance(locale, str):
            super().__init__([locale])
        else:
            super().__init__(self.clean(locale))
        self._requested = None

    def __eq__(self, other):
        if isinstance(other, str):
            return len(self) == 0 or self[0] == other
        return super().__eq__(list(other))

    @property
    def requested(self):
        """Return the locales that were originally requested.
        
        This is useful if the localization .ftl files are switched and the
        originally requested locales shall be matched against the new .ftl
        files again.
        """
        return self if self._requested is None else Locale(self._requested)

    @classmethod
    def auto(cls, fallback: str = None, count: int = 10):
        """Automatically select the most preferable locales for the user.

        Selects the most preferable locales for the user that are currently available.
        
        Args:
            index_url: The URL to the index.lst file containing a list of all available
                locales (one locale per line). If not given, the default index.lst
                file will be used.
            fallback: The locale to use if the operation fails. If not given, the
                default fallback locale will be used.
            count: The maximum number of fallback locales to use.
        """
        from fluent_anvil.registries import LocaleIndex
        fallback = fallback or cls.fallback
        try:
            index = cls.clean(LocaleIndex(cls.index_url))
        except HttpError:
            return cls(fallback)

        requested = cls.clean(cls.preferred(fallback))
        obj = cls(cls.match(requested, index, fallback, count))
        obj._requested = requested
        return obj

    @classmethod
    def select(cls, available: list):
        """Select the user's most preferred locale given the available locales.
        
        Args:
            available: List of locales available.
        """
        import anvil.server
        is_server = anvil.server.context.type == "server_module"
        available = [available] if isinstance(available, str) else list(available)
        requested = cls.clean(cls.fallback) if is_server else cls.clean(cls.preferred())
        obj = cls(cls.match(requested, available, count=1))
        obj._requested = requested
        return obj

    @classmethod
    def _match_py(cls, requested: list, available: list, fallback: str, count: int):
        from .langcodes import closest_match
        locales = []
        for index, loc in enumerate(requested):
            if len(locales) < count:
                lang, dist = closest_match(loc, available, max_distance=cls.max_distance)
            if lang not in locales and dist <= cls.max_distance:
                locales.append(lang)
        return Locale(locales)

    @classmethod
    def _match_js(cls, requested: list, available: list, fallback: str, count: int):
        from .js import fluent_js
        return Locale(fluent_js.match_locale(requested, available, fallback, count))
    
    @classmethod
    def match(cls, requested: list, available: list = None, fallback: str = None, count: int = 10, force_py = False):
        """For the given requested locales, return the best matching available locales.

        Given a list of requested locales and locales available (i.e. those supported by 
        the application), the method returns an ordered list of available locales that 
        best fit any of the requested locales. The first locale in the returned list is 
        the one with the best fit. If there is no sensible match, the fallback is 
        returned (e.g., the application's primary / best supported language or a widely 
        spoken locale like English).

        Args:
            requested: A single locale or a list of locales that the user prefers.
            available: A list of locales that the application supports. If not given, 
                the default index.lst file will be used.
            fallback: The locale to return if no sensible match is found. If not given, 
                the default fallback locale will be used.
            count: The maximum number of fallback locales to use.
            force_py: Force the use of the Python implementation of the matching
                algorithm instead of the JavaScript one.
        """
        from fluent_anvil.registries import LocaleIndex
        import anvil.server
        available = LocaleIndex(cls.index_url) if available is None else available
        fallback = cls.clean(fallback or cls.fallback) 

        available = cls.clean([available] if isinstance(available, str) else available)
        requested = cls.clean([requested] if isinstance(requested, str) else requested)      

        is_server = anvil.server.context.type == "server_module"
        obj = (
            cls._match_py(requested, available, fallback, count) 
            if is_server or force_py else 
            cls._match_js(requested, available, fallback, count)
        )
        obj._requested = cls.clean(requested)
        return obj
    
    @classmethod
    def preferred(cls, fallback: str = None) -> list:
        """Return the user's preferred locales.

        Uses the Get-User-Locale library https://github.com/wojtekmaj/get-user-locale .
        
        Args:
            fallback: The fallback locale to return if operation fails. If not given, 
                the default fallback locale will be used.
        """
        import anvil.js
        from fluent_anvil.js import ASSET_URL, FLUENT_LIB
        fluent_js = anvil.js.import_from(f"{ASSET_URL}{FLUENT_LIB}")
        fallback = cls.clean(fallback or cls.fallback)
        return cls(fluent_js.get_user_locales(fallback))
    
    @classmethod
    def clean(cls, locale):
        """Ensure valid IETF language tags.

        Since Anvil does not support hyphens for directories, users may use an 
        underscore for the locale names as well. However, this would not be valid IETF 
        language tags. Therefore, replace any underscores with hyphens. The JavaScript 
        library will switch to underscore again when loading the assets.

        Args:
            locale: String or iterable of locale strings, e.g., "en-US".
        """
        if locale is None:
            return None
        if isinstance(locale, str):
            return locale.replace("_", "-")
        return [cls.clean(e) for e in locale]
    
    def decompose(self, index: int = 0) -> dict:
        """Decompose the locale or one of its fallbacks into its components.

        Decompose the locale (index = 0) or one of its fallbacks (index > 0) into its
        components. Returns a dictionary which contains the locale's components as keys 
        and the corresponding values as dictionary values.
        """
        loc = self[index].replace("_", "-").strip().split("-")
        decomp = {}

        for i, entry in enumerate(loc):
            if i == 0:
                decomp["language"] = entry
            elif len(entry) == 3 and entry == entry.lower():
                decomp["extlang"] = entry
            elif len(entry) == 4 and entry == entry.title():
                decomp["script"] = entry
            elif (len(entry) == 2 and entry.isalpha()) or (len(entry) == 3 and entry.isnumeric()):
                decomp["region"] = entry
            elif len(entry) >= 4 and entry == entry.lower():
                decomp["variant"] = entry
            elif len(entry) == 1 and entry[0] == "u":
                decomp["extension"] = loc[i:]
            elif len(entry) == 1 and entry[0] == "x":
                decomp["privateuse"] = loc[i:]
            else:
                raise Exception(f'Cannot identify "{entry}" subtag in "{self[index]}".') 
        return decomp
    
    @classmethod
    def compose(cls, pattern: dict, components: dict):
        """Create a locale given a pattern and its components."""
        def info(args: list):
            args = [e for e in args if e is not None]
            if len(args) > 1:
                pat = pattern["localeSeparator"]
                outp = pat.replace("{0}", args[0]).replace("{1}", info(args[1:]))
                return outp.strip()
            return "" if not args else args[0]
        extra = info([
            components.get("variant", None),
            components.get("script", None),
            components.get("region", None),
        ])

        if not extra:
            return components["language"]
        sep = pattern["localePattern"]
        return cls(sep.replace("{0}", components["language"]).replace("{1}", extra))
    
    def __repr__(self):
        locales = ", ".join(self[1:]) if len(self) > 0 else "0 fallbacks"
        return f"<Locale {self[0]} ({locales})>"
    
    def __str__(self):
        return ", ".join(self)
