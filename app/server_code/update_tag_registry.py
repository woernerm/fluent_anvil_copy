"""This file defines background task(s) to update the subtag registry for available localereg.

As of 2023-05-06 there is now standardized way in JavaScript to determine what tags
would be available on the client machine. Using get Intl.DisplayNamereg.supportedLocalesOf()
only provides a filtered list of what the client would support given an initial list
of localereg. However, this initial list of locales can not be acquired using JavaScript.

Fortunately, there is an official language tag registry available here:
https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry
The background task(s) defined here can be executed regularly to download and
parse the registry. Loading and parsing the data on the client side would take
way too long wasting precious seconds of loading time. Instead, the data is loaded
and parsed in advance into a simple list of short tags and stored in the app's
database. An explaination of how the IANA subtag registry is read, can be found
here: https://www.w3.org/International/articles/language-tags/
"""

from datetime import datetime, timedelta
from anvil.tables import app_tables
from .registries import IANASubtagRegistry, LocalSubtagRegistry, CLDRFile, CLDRLocale
import anvil.server

REGISTRY_MAX_AGE = timedelta(days=30)
        
@anvil.server.background_task
def task_update_subtag_registry():
    local_reg = LocalSubtagRegistry()
    age = datetime.now().astimezone() - local_reg.get_updated_on()
    if age <= REGISTRY_MAX_AGE:
        return
        
    ## Update IANA subtag registry
    registry = IANASubtagRegistry()
    updated_on = registry.updated_on
    
    for typename in registry.get_types():
        subtags = registry.get_by_type(typename)
        local_reg.update_or_create(typename, subtags, updated_on)

    local_reg.update_or_create(
        registry.SUPPRESS_SCRIPT, 
        registry.get_suppressed_scripts(), 
        registry.updated_on
    )

    ## Update locale registry
    LOCALE_NAME_DIR = "cldr-json/cldr-localenames-full/main/en"
    updated_on = datetime.now().astimezone()
    locales = CLDRLocale.find_locales()
    cldr = CLDRLocale(LOCALE_NAME_DIR)
    translated = {key: cldr.format(key) for key in locales}
    translated = {k: v for k,v in translated.items() if v is not None}
    local_reg.update_or_create("locale", translated, updated_on)


    ## Update currency registry
    CURRENCY_FILE = "cldr-json/cldr-numbers-full/main/en/currencies.json"
    file = CLDRFile(CURRENCY_FILE)
    currencies = file.drill("main", "en", "numbers", "currencies")
    currencies = {k: v.get("displayName", None) for k, v in currencies.items()}
    local_reg.update_or_create("currency", currencies, updated_on)
    
@anvil.server.callable
def launch_registry_update():
    anvil.server.launch_background_task('task_update_subtag_registry')
    
