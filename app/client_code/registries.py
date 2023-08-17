from datetime import datetime
from anvil.http import request, HttpError
from anvil.tables import app_tables, Transaction
from json import loads, dumps

class JSONDB:

    def __init__(self):
        import anvil.server
        self._url = f"{anvil.server.get_app_origin()}/_/theme/registry/fluent_subtag_registry"+"_{typename}.json"
        self._content = {}

    def _load(self, typename):
        if typename in self._content:
            return self._content[typename]
        filename = self._url.format(typename=typename)
        response = request(filename) 
        self._content[typename] = loads(response.get_bytes().decode("utf-8"))
        return self._content[typename]
    
    def get(self, **kwargs):
        cont = self._load(kwargs.get("type", ""))
        return next((row for row in cont if all(row.get(ck) == cv for ck, cv in kwargs.items())))

    def search(self, **kwargs):
        cont = self._load(kwargs.get("type", ""))
        return [row for row in cont if all(row.get(ck) == cv for ck, cv in kwargs.items())]
    

def get_subtag_registry():
    from fluent_anvil.exceptions import NoSubtagRegistry
    if not hasattr(app_tables, "fluent_subtag_registry"):
        raise NoSubtagRegistry(
            'You need to define a table called "fluent_subtag_registry" first. '
            'It has to have three columns: Text column named "type", '
            'simple Object column named "subtags", and a date and time '
            'column named "updated_on".'
        )
    return app_tables.fluent_subtag_registry


class IANASubtagRegistry:
    """Class that represents the IANA Language Tag Registry.
    
    Its purpose is to load the data from the subtag registry and parse it.
    """
    DELIMITER = "%%"
    SUBTAG = "subtag"
    TYPE = "type"
    REGION = "region"
    LANGUAGE = "language"
    SCRIPT = "script"
    VARIANT = "variant"
    SUPPRESS_SCRIPT = "suppress-script"
    DEPRECATED = "deprecated"
    PREFERRED_VALUE = "preferred-value"
    DESCRIPTION = "description"
    PRIVATE_USE = "private use"

    URL_LANGUAGE_TAG_REGISTRY = "https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry"
    """The URL to the IANA Language Tag Registry

    This is needed to provide a complete list of supported language tags.
    A nice description of what each element in that registry means can be found
    here: https://www.w3.org/International/articles/language-tags/
    """
    
    def __init__(self):
        self._updated_on = datetime.now().astimezone()
        # Download the language tag registry. Fortunately,
        # this is just a text file with no authentication required.
        response = request(self.URL_LANGUAGE_TAG_REGISTRY)
        self._content = response.get_bytes().decode("utf-8").splitlines()
        self._lastkey = None
        self._entry = {}
        self._data = None

    @property
    def updated_on(self):
        return self._updated_on

    @property
    def data(self):
        if self._data is None:
            self._data = [e for e in self]
        return self._data

    def _parse_line(self, line: str):
        # Is the line a continuation of the previous line?
        if line.startswith("\t") or line.startswith(" "):
            self._entry[self._lastkey] += f" {line}"
        else:
            key, value = line.split(":", 1)
            self._lastkey = key.lower().strip()
            self._entry[self._lastkey] =  value.strip()

    @classmethod
    def _isvalid(cls, entry: dict):
        return (
            cls.TYPE in entry and 
            cls.SUBTAG in entry and 
            cls.PREFERRED_VALUE not in entry and
            cls.DEPRECATED not in entry and
            entry.get(cls.DESCRIPTION, "").lower() != cls.PRIVATE_USE
        )
        
    def __iter__(self):
        self._lastkey = None
        self._entry = {}
        for line in self._content:
            if line.startswith(self.DELIMITER):
                if self._entry and self._isvalid(self._entry):
                    yield {**self._entry}
                self._entry.clear()
                self._lastkey = None
                continue
            self._parse_line(line)

    def get_by_type(self, typename: str):
        return {e[self.SUBTAG]: e[self.DESCRIPTION] for e in self.data if e[self.TYPE] == typename}

    def get_types(self):
        return {e[self.TYPE] for e in self.data}

    def get_suppressed_scripts(self):
        return {e[self.SUBTAG]: e[self.SUPPRESS_SCRIPT] for e in self.data if e.get(self.SUPPRESS_SCRIPT, None)}


class LocalSubtagRegistry:
    """Class that represents the app's tag registry.
    
    Its purpose is to store and load the data from the app's tag registry.
    """
    COL_TYPE = "type"
    COL_SUBTAGS = "subtags"
    COL_UPDATED_ON = "updated_on"

    def __init__(self, use_json: bool = False):
        self.db = JSONDB() if use_json else get_subtag_registry()

    def update_or_create(self, typename: str, subtags: dict, updated_on: datetime):
        data = {
            self.COL_TYPE: typename, 
            self.COL_SUBTAGS: subtags, 
            self.COL_UPDATED_ON: updated_on
        }
    
        with Transaction() as txn:
            row = self.db.get(type = typename)
            self.db.add_row(**data) if row is None else row.update(**data)

    def get_updated_on(self, typename: str = None) -> datetime:
        if typename:
            row = self.db.get(**{self.COL_TYPE: typename})
            return None if row is None else row.get("updated_on", None)   
        return min([e['updated_on'] for e in self.db.search()])     

    def get_tags(self, typename: str):         
        row = self.db.get(**{self.COL_TYPE: typename})
        if not row:
            raise LookupError("No locale data available.")
        return row.get(self.COL_SUBTAGS)

    def download_json(self, typename: str):
        data = [{"type": e["type"], "subtags": e["subtags"], "updated_on": e["updated_on"].isoformat()} for e in self.db.search(type=typename)]
        blob = anvil.BlobMedia('text/plain', dumps(data).encode("utf-8"), name=f'fluent_subtag_registry_{typename}.json')
        anvil.media.download(blob)

    def get_descriptions(self, code: str, typename: str):
        codes = [code] if isinstance(code, str) else code
        row = self.db.get(**{self.COL_TYPE: typename})
        if not row:
            raise LookupError("No locale data available.")
        data = row.get(self.COL_SUBTAGS, {})
        return [data[tag] for tag in codes]


class CLDRFile:
    """Base class that represents a file in the CLDR repository.
    
    Its purpose is to load and parse a json file from the CLDR repository.
    After initialization it can be used like a dictionary.
    """

    URL_CLDR_RAW = "https://raw.githubusercontent.com/unicode-org/cldr-json/main/"
    """The URL to the raw files of the CLDR json repository.

    This is used for appending the relative repository path in order to
    get the complete url. The CLDR-Repository can be found here:
    https://github.com/unicode-org/cldr-json/tree/main
    """

    URL_CLDR_CONTENT = "https://api.github.com/repos/unicode-org/cldr-json/contents/"
    """API url for obtaining directory contents in the cldr github repository."""
    
    def __init__(self, path: str):
        from fluent_anvil.exceptions import NotFound
        self._url = self.URL_CLDR_RAW + path
        # Download the language tag registry. Fortunately,
        # this is just a text file with no authentication required.
        try:
            self._requested_on = datetime.now().astimezone()
            response = request(self._url)
            self._content = loads(response.get_bytes().decode("utf-8"))
        except HttpError as e:
            if e.status == 404:
                raise NotFound(f'Unable to load "{self._url}"')
            raise e

    @property
    def url(self):
        return self._url

    @property
    def requested_on(self):
        return self._requested_on

    def __getitem__(self, element):
        return self._content[element]

    def get(self, index, default = None):
        return self._content.get(index, default)

    def drill(self, *keys):
        for i, key in enumerate(keys):
            data = data.get(key, {}) if i else self._content.get(keys[0], {})
        return data

    @classmethod
    def listdir(cls, path: str) -> list:
        """Returns the contents of the given path in the cldr repository.
        """
        upath = path[:-1] if path.endswith("/") else path
        url = f"{cls.URL_CLDR_CONTENT}{upath}?ref=main"
        response = request(url)
        content = loads(response.get_bytes().decode("utf-8"))
        return [(e["name"], e["type"].lower(),) for e in content]


class CLDRLocale:
    """Class that represents a single locale from the cldr json github repository."""

    FILE_LANGUAGES = "languages.json"
    """The name of the file that contains language names."""

    FILE_TERRITORIES = "territories.json"
    """The name of the file that contains region names."""

    FILE_SCRIPTS = "scripts.json"
    """The name of the file that contains script names."""

    FILE_VARIANTS = "variants.json"
    """The name of the file that contains language variant names."""

    FILE_DISPLAY = "localeDisplayNames.json"
    """The name of the file that contains locale display format."""

    COL_LOCALE = "locale"
    """Column name for the locale translations."""

    COL_LANGUAGES = "languages"
    """Column name for the language translations."""

    COL_REGIONS = "regions"
    """Column name for the region translations."""

    COL_SCRIPTS = "scripts"
    """Column name for the script translations."""

    COL_VARIANTS = "variants"
    """Column name for the variant translations."""

    COL_PATTERNS = "patterns"
    """Column name for the locale patterns."""

    COL_UPDATED_ON = "updated_on"
    """Column name indicating when the data was last updated."""

    LOCALE_NAME_DIR = "cldr-json/cldr-localenames-full/main/"
    """Directory in which locale translations are stored."""
    
    def _get(self, filename: str, *relpath):
        from fluent_anvil.exceptions import NotFound
        """Returns information in the given file at the given position in the json treee.

        Since all files always start with the "main", locale key, and "localeDisplayNames",
        the given relpath does not have to provide these.
        """
        try:
            file = CLDRFile(self._locale_dir + filename)
            return file.drill("main", self._locale, "localeDisplayNames", *relpath)  
        except NotFound:
            return {}

    def __init__(self, locale_dir: str):
        self._locale_dir = locale_dir if locale_dir.endswith("/") else f'{locale_dir}/'
        self._locale = self._locale_dir[self._locale_dir[:-1].rfind("/")+1:-1]
        self._updated_on = datetime.now().astimezone()

        self._patterns = self._get(self.FILE_DISPLAY, "localeDisplayPattern")
        self._languages = self._get(self.FILE_LANGUAGES, "languages")
        self._regions = self._get(self.FILE_TERRITORIES, "territories")
        self._variants = self._get(self.FILE_VARIANTS, "variants")
        self._scripts = self._get(self.FILE_SCRIPTS, "scripts")
        
        self._variants = {k.lower(): v for k, v in self._variants.items()}
        self._scripts = {k.title(): v for k, v in self._scripts.items()}
        self._languages = {k.lower(): v for k, v in self._languages.items()}
        self._regions = {k.upper(): v for k, v in self._regions.items()}

    @classmethod
    def find_locales(cls):
        locales = CLDRFile.listdir(cls.LOCALE_NAME_DIR)
        return [name for name, tp in locales if tp == "dir"]

    def format(self, locale:str) -> str:
        def translate(registry: dict, components: dict, key: str):
            return {key: registry.get(components.get(key, None), None)}
        
        dec = Locale(locale).decompose() 
        return Locale.compose(self.patterns, {
            **translate(self.languages, dec, "language"),
            **translate(self.regions, dec, "region"),
            **translate(self.variants, dec, "variant"),
            **translate(self.scripts, dec, "script"),
        })
        
    @property
    def patterns(self):
        return self._patterns

    @property
    def languages(self):
        return self._languages

    @property
    def regions(self):
        return self._regions

    @property
    def variants(self):
        return self._variants

    @property
    def scripts(self):
        return self._scripts

    @property
    def locale(self):
        return self._locale

class LocaleIndex(list):
    """Represents an index.lst file that lists all locales available."""

    def __init__(self, index_url):
        try:
            response = request(index_url)
            locales = response.get_bytes().decode("utf-8").split("\n")
            cleaned = list({e.strip().replace("_", "-") for e in locales})
            super().__init__(cleaned)
        except HttpError as e:
            raise HttpError(f'URL "{index_url}": {e}') from e
        