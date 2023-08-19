# FluentAnvil

## Introduction
Make your [Anvil](https://anvil.works/) app appeal to users all around the world by
serving high-quality translations and displaying dates and numbers the way your users
expect. With FluentAnvil, this becomes a breeze!

The library serves as a Python interface to [Fluent](https://projectfluent.org/). It is 
a localization system developed by Mozilla for natural-sounding translations. In 
contrast to gettext you can create more nuanced and natural sounding translations. This
is because fluent does not assume a one-to-one mapping between the original language
(often English) and the translation. For example, Polish has more plural forms than 
English or German. Therefore, selecting the right translation requires knowing how many 
there are of something. With localization systems like gettext, this requires adding 
additional logic inside your application. With Fluent, this language-specific logic is 
encapsulated in the translation file and does not impact other translations.

Personally, I think the greatest thing about Fluent apart from the translation quality 
is that it is easier to learn and use than gettext: It uses only one simple text file 
format (.ftl) and does not require specialized extraction tools. Often, translations are 
as simple as this:

en_US/main.ftl:
```
close-button = Close
```
de_DE/main.ftl:
```
close-button = Schließen
```

For simple translations, the syntax stays simple: Define a message id like 
`close-button` and provide the translation after the equal sign. If a translation 
happens to be more complicated for a language, you only need to add the logic in the 
translation file for that particular language. You can find out more at 
[Project Fluent](https://projectfluent.org/).
The translation happens entirely on the client side. Therefore, it works on 
[Anvil's free plan](https://anvil.works/pricing) as well since there is no need to 
install a special package.

You can put the .ftl translation files into a directory as part of your app's assets.
The library will automatically select and load the translation file that the user   
prefers most based on the client's browser settings.

Please note that this is a personal project with the hope that it may be of use to 
others as well. I am neither affiliated with 
[Project Fluent](https://projectfluent.org/) nor [Anvil](https://anvil.works/).

## Documentation
You can find the [complete documentation here](https://woernerm.github.io/fluent_anvil/).

## Quick Guide
### Installation
All you need to do is log into your Anvil account and add it as a third-party dependency 
with the token `UHLC7WE6TELL25TO` .

### IETF language tags
Languages can come in many variants. For example, English is spoken and written slightly 
differently depending on where you are. There is British English, Canadian English, 
American English, and many others. In order to identify these languages on the Internet, 
standardized codes are used, e.g., "en-US" identifies English as spoken in the United 
States and "zh-Hant-HK" identifies Traditional Chinese as used in Hong Kong. Such a code 
is called [IETF language tag](https://en.wikipedia.org/wiki/IETF_language_tag). These 
tags are composed of subtags identifying the primary language (e.g., "en" for English), 
the regional variant of a language (e.g., "US" for United States), the script (e.g., 
"Latn" for Latin or "Taml" for Tamil), and other aspects that make up a specific 
language variant. 
Apart from the primary language tag, all other tags are optional and should be used only 
to add distinguishing information. The tags are there to serve YOUR needs. Therefore, 
you can add subtags depending on what YOU need. Therefore, if your app is translated 
only into a couple of languages, the primary language tag might suffice to uniquely 
identify all your translations. For more detail, you can find a great explanation by 
the World Wide Web Consortium 
[here](https://www.w3.org/International/articles/language-tags/). 

### Translation
In Anvil's assets section, add a directory to place your translations in, ideally you 
have one subfolder for each locale, e.g.
- localization
     - es_MX
         - main.ftl
     - en_US
         - main.ftl
     - de_DE
         - main.ftl
     - index.lst

With Fluent, you can use variables for placeholders or selecting the appropriate 
translation. In the following example we are going to greet the user. Therefore, we use 
a variable as a placeholder for the user's name. Assume that the content of 
es_MX/main.ftl is: `hello = Hola { $name }.`

Then, import the fluent singleton object and the Message class in your form (Message is 
optional but required for the examples):
```py
from fluent_anvil.lib import fluent, Message
```
If you want to know which locale the user prefers, just call
```py
fluent.get_preferred_locales()
```
This will return a list of locales such as `['de-DE']` that the user prefers (this 
method does not use Fluent but the 
[get-user-locale](https://www.npmjs.com/package/get-user-locale) package).

Now, you can configure Fluent using the following (we ignore the preferred locale for 
now):
```py
fluent.configure(
    ["es-MX"], 
    "{locale}/main.ftl", 
    "./_/theme/localization/",
    "index.lst"
)
```
This will tell fluent to use the Mexican Spanish locale. The first parameter is a list 
of desired locales. Locales are given in the order of preference (most preferable 
first). This means, Fluent will always try the first locale in the list when trying to 
find a translation. If a translation is not available for that locale, Fluent will try 
the others until a suitable translation has been found. The second parameter is a 
template string indicating where the translation files are stored relative to a root
directory (third argument). The placeholder {locale} is replaced with the desired locale 
(hyphens are converted to underscores, because Anvil does not allow hyphens in directory 
names). The `fluent.configure()` method accepts locales regardless of whether you use 
hyphens or underscores. You can also provide None for the locale so that FluentAnvil
will choose a locale automatically based on what the user most likely prefers:
```py
fluent.configure(
    None, 
    "{locale}/main.ftl", 
    "./_/theme/localization/",
    "index.lst"
)
```
The settings chosen in the above example are actually the default. So, if you
put your translation files into a folder named `localization` as part of your app's
assets, then you don't have to configure anything. The last parameter is the relative
path to a file named index.lst. The default assumes that this file is located directly
in the `localization` folder. It contains a simple list of all locales available:
localization/index.lst:
```
de-DE
en-US
es-MX
```
Again, it does not matter whether you use hyphen or underscore.

It makes sense to structure your translations into multiple files (e.g., you could have
a separate file for each form). You can provide path templates to all .ftl files as
a list:
```py
files = [
    "{locale}/main.ftl",
    "{locale}/profile_settings.ftl",
    "{locale}/my_subform.ftl"
]
fluent.configure(templates=files)
```

Now, you can greet the user:
```py
print(fluent.format("hello", name="John"))
```
Every variable you want to have access to in your .ftl files can be added as a keyword 
variable. Apart from facts like the user's name this can be used to determine a natural 
sounding translation. These variables may include the count of something or the 
time of day. Depending on the type of variable, Fluent will automatically format the 
value according to the selected locale. For example, these messages:
en_US/main.ftl:
`time-elapsed = Time elapsed: { $duration }s.`
and
de_DE/main.ftl:
`time-elapsed = Vergangene Zeit: { $duration }s.`
After calling a command like
```py
print(fluent.format("time-elapsed", duration=12342423.234))
```
the message will show up with locale `en-US` as:
`Time elapsed: ⁨12,342,423.234⁩s.`
While with locale "de_DE" it will show up as:
`Vergangene Zeit: ⁨12.342.423,234⁩s.`
Pay attention to the use of dot and comma which is specific to the respective countries.

You can translate multiple strings at once (that is more efficient than one by one) by 
wrapping them in Message objects:
```py
print(fluent.format(
    Message("hello", name="World"), 
    Message("welcome-back", name="John"),
    ...
))
```
This returns a list of all translations in the same order as the corresponding Message 
instances.

You can switch to a different locale on the fly using the `locale` property. Again, the 
first list element is the desired locale and the remaining entries in the list are 
fallback locales in case the translation searched for is not available for the desired 
locale.
```py
fluent.locale = ["en-US", "en-GB", "en-AU"]
```
Although this is completely equivalent to 
`fluent.configure(["en-US", "en-GB", "en-AU"])`, its meaning is more obvious when 
reading code.

### Localized Formatting
You can also use FluentAnvil to format numbers and dates like this:

```py
import datetime

# Print the number 32000 the way it is written in the USA.
fluent.locale = ["en-US"]
print(fluent.format(320000)) # Displayed as: 320,000

# Print the number 32000 the way it is written in Germany.
fluent.locale = ["de_DE"]
print(fluent.format(320000)) # Displayed as: 320.000

mydate = datetime.datetime.fromisoformat("2011-11-04T03:05:23")

# Print the date 2011-11-04T03:05:23 the way it is written in the USA.
fluent.locale = ["en_US"]
print(fluent.format(mydate)) # Displayed as: Nov 4, 2011, 3:05:23 AM

# Print the date 2011-11-04T03:05:23 the way it is written in Germany.
fluent.locale = ["de_DE"]
print(fluent.format(mydate)) # Displayed as: 04.11.2011, 03:05:23

mydate = datetime.time.fromisoformat("04:23:01")

# Print the time 04:23:01 the way it is written in the USA.
fluent.locale = ["en_US"]
print(fluent.format(mydate)) # Displayed as: 4:23 AM

# Print the time 04:23:01 the way it is written in Germany.
fluent.locale = ["de_DE"]
print(fluent.format(mydate)) # Displayed as: 04:23
```

If you have special requirements regarding the way dates and numbers shall be formatted,
you have various options for customization at your disposal. As above, you can provide
these using `fluent.configure()`. For example:
```py
fluent.configure(
    # Make dates really long and verbose.
    datetime_options = {
        "dateStyle": "full", 
        "timeStyle": "full",
    },
    # Use scientific notation and always display the sign.
    number_options = {
        "notation": "scientific",
        "signDisplay": "always"
    }
)
```
With that, the previous example becomes:
```py
import datetime

# Print the number 32000 the way it is written in the USA.
fluent.locale = ["en-US"]
print(fluent.format(320000)) # Displayed as: +3.2E5

# Print the number 32000 the way it is written in Germany.
fluent.locale = ["de_DE"]
print(fluent.format(320000)) # Displayed as: +3,2E5

mydate = datetime.datetime.fromisoformat("2011-11-04T03:05:23")

# Print the date 2011-11-04T03:05:23 the way it is written in the USA.
fluent.locale = ["en_US"]
print(fluent.format(mydate)) # Displayed as: Friday, November 4, 2011 at 3:05:23 AM Central European Standard Time

# Print the date 2011-11-04T03:05:23 the way it is written in Germany.
fluent.locale = ["de_DE"]
print(fluent.format(mydate)) # Displayed as: Freitag, 4. November 2011 um 03:05:23 Mitteleuropäische Normalzeit
```

Internally, FluentAnvil uses JavaScript's Intl.DateTimeFormat and Intl.NumberFormat
functionality. Therefore, you can find a complete documentation of all options here:

* [Options for numbers](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat/NumberFormat)
* [Options for dates and times](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat/DateTimeFormat)

### Keeping Translation Code Short and Expressive
You often have various data structures that require translation. These include
Anvil component attributes, lists, dictionaries, and combinations of these. With 
FluentAnvil you can translate them on the fly without the need to unpack, translate and 
repack them again. Some examples are given in the following.

#### Dictionaries
The format() method also works with dictionaries for which it will translate the values:
```py
fluent.format({
        "my key 1": "my-fluent-message",
        "my key 2": "my-other-fluent-message"
    })
```

#### Anvil Components
One of my favorite features is the possibility to write directly to GUI component 
attributes:
```py
fluent.format(
    Message("hello", name="world"), 
    Message(self.label, "text", "hello", name="John"),
)
```
You just provide the component and the name of the attribute you want to write to 
(like Python's `setattr()` function).

#### Lists of Dictionaries (Anvil Extras MultiSelectDropdown)
Lists of dictionaries are commonly used to model tables: The list entries represent 
rows, and each dictionary entry represents a named column. You can translate these using
the `format_table()` method. In the following example we are going to translate the 
names of time units. The data structure is typical to what the
[MultiSelectDropdown from the Anvil Extras package](https://anvil-extras.readthedocs.io/en/latest/guides/components/multi_select_dropdown.html)
expects:
 
```py
options = [
    {"value": "nanosecond", "key": "unit-nanosecond"},
    {"value": "microsecond", "key": "unit-microsecond"},
    {"value": "millisecond", "key": "unit-millisecond"},
    {"value": "second", "key": "unit-second"},
    {"value": "minute", "key": "unit-minute"},
    {"value": "hour", "key": "unit-hour"},
    {"value": "day", "key": "unit-day"},
    {"value": "week", "key": "unit-week"},
    {"value": "year", "key": "unit-year"}
]

translated_options = fluent.format_table(options, ["key"], my_contenxt_var = "my context")
```
The second parameter is a list of keys to translate. Fluent-Anvil assumes that the value 
of every given key represents a Fluent message id. Other keys and their values will not 
be touched and returned as-is.
Context variables can be provided as keyworded arguments or omitted completely. For 
example, consider you selected "de_DE" as locale and had someone provide you with the 
corresponding .ftl file, the result might look like this:

```py
translated_options = [
    {"value": "nanosecond", "key": "Nanosekunde"},
    {"value": "microsecond", "key": "Mikrosekunde"},
    {"value": "millisecond", "key": "Millisekunde"},
    {"value": "second", "key": "Sekunde"},
    {"value": "minute", "key": "Minute"},
    {"value": "hour", "key": "Stunde"},
    {"value": "day", "key": "Tag"},
    {"value": "week", "key": "Woche"},
    {"value": "year", "key": "Jahr"}
]
```

### Bonus Round: Translate your HTML Templates
You can translate your static content as well. Just add the tags `data-l10n-id` for the 
message id and `data-l10n-args` for context variables (if needed) like this:
```html
<h1 id='welcome' data-l10n-id='hello' data-l10n-args='{"name": "world"}'>Localize 
me!</h1>
```
If you do not initialize a Fluent instance, you will see "Localize me!". As soon as the 
Fluent instance is initialized (e.g., with locale es-MX), the text changes to 
"Hola ⁨world⁩". If Fluent would fail for some reason, the default text (in
this case "Localize me!") would be shown.

## Validation
An essential part of a good user interface is proper input validation. This requires
that you provide feedback to the user in a language the user understands. Fluent-Anvil
has you covered there as well: The validator module defines a `Validator` class with
which you can define a translated validation procedure. 

Consider a datepicker called `my_datepicker` that allows the user to define a deadline 
for a task. We want to validate that the selected date is not in the past. Otherwise, a 
message informing the user about the invalid date shall be shown using a label component 
called `my_label`. A solution might look like this:

```py
from fluent_anvil.lib import Validator
from datetime import datetime

deadline_validator = Validator(
    lambda value: value >= datetime.now().astimezone(),
    "deadline-in-the-past",
    my_context_var = "my context"
)
```

The Validator initialization method only requires two parameters:
* A function that returns True if the value to be validated passed the validation test. 
False, otherwise. Alternatively, it may also be a 
[Zod validator from Anvil Extras](https://anvil-extras.readthedocs.io/en/latest/guides/modules/zod.html).
* A Fluent message id that represents an explanatory message to the user if validation
fails.

In the Form class of the Anvil app, we can define a change event for the datepicker in
which validation is performed:

```py
from ._anvil_designer import EditDateTemplate
from fluent_anvil.lib import ValidationError

# Some other code like the definition of deadline_validator.

class EditDateForm(EditDateTemplate):

    # Some other code

    def my_datepicker_change(self, **event_args):
        try:
            deadline_validator.validate(self.my_deadline.value)
            self.my_label.text = ""
        except ValidationError as error:
            self.my_label.text = str(error)
```
The `validate(value, *args, **kwargs)` method calls the lambda function defined earlier. 
The validation function is not limited to a single parameter. You can define an 
arbitrary validation function signature as long as it has at least one required 
parameter. You then provide all required parameter values to 
`validate(value, *args, **kwargs)` which in turn passes them on to your validation 
function.

If validation succeeds, nothing happens. In the above example, the label text is set to 
an empty string. If validation fails, a ValidationError is thrown. The exception message 
will contain the desired translation corresponding to the message id 
`"deadline-in-the-past"` as defined earlier.

Multiple validation steps can be chained by alternately providing validation function 
and Fluent message id during initialization of the Validator class like this:
```py
from fluent_anvil.lib import Validator

text_length_validator = Validator(
    lambda text: len(text) > 10,
    "text-too-short",
    lambda text: len(text) < 120,
    "text-too-long",
    my_context_var = "my context"
)
```
When calling `validate(value, *args, **kwargs)` the validation functions are called
one after another. In the above example, it is first checked whether the text is long
enough. After that, it is checked whether the text is short enough. As usual, optional 
context variables can be passed on to the Fluent translation string by providing them as 
keyworded arguments.

Validator objects are callable. This is useful if you do not want to throw an 
exception:
```py
from ._anvil_designer import EditDateTemplate
from fluent_anvil.lib import ValidationError

# Some other code like the definition of deadline_validator.

class EditDateForm(EditDateTemplate):

    # Some other code

    def my_datepicker_change(self, **event_args):
        self.my_label.text = deadline_validator(self.my_deadline.value, "")
```
If the provided value passes validation, the given default value is returned (usually 
an empty string, None, or some other special value). Otherwise, the translated error 
message is returned.

So, should you use `my_validator.validate(value, *args, **kwargs)` or 
`my_validator(value, default, *args, **kwargs)`? This depends on what you want to do
in case validation fails. If you just want to display a message, call the
validator. If you want to do several things at once like showing the message and
changing the role of a component (e.g., to highlight the text box for which
validation failed), use `my_validator.validate(value, *args, **kwargs)` in a 
try...except block as shown in the first example.

### Predefined Validators
Some validation tasks occur more often than others. In this section, some predefined
classes for validation will be presented. Over time, this section may grow.

#### LengthValidator
The `LengthValidator` class is useful for validating data that supports `len()`. 
Primarily, it is intended to validate that some text is neither too short nor too long.
However, you can use it for lists and tuples just as well.
```py
from ._anvil_designer import EditTextTemplate
from fluent_anvil.lib import LengthValidator

min_length = 10
max_length = 120

text_length_validator = LengthValidator(
    min_length, max_length,
    "text-too-short",
    "text-too-long",
    my_context_var = "my context"
)

class EditTextForm(EditTextTemplate):

    # Some other code

    def validate_form(self, save: bool):
        try:
            text_length_validator.validate(self.my_text.text, save)
            self.my_label.text = ""
        except ValidationError as error:
            self.my_label.text = str(error)

    def on_text_area_lost_focus(self, **event_args):
        self.validate_form(False)

    def on_save_button(self, **event_args):
        self.validate_form(True)
```
The first two parameters of `LengthValidator.__init__()` denote the minimum and maximum 
length of the text, respectively. The next two parameters denote the error message ids 
for a text that is too short and for a text that is too long. Finally, keyworded 
context variables can be added as usual. In case you do not need to validate the minimum 
or maximum length, you can set the corresponding parameter to None. Validation will then 
always succeed for that characteristic.
The `validate()` function and `__call__` dunder have an optional second parameter that
determines whether the minimum length is enforced. This is useful if enforcing the
minimum length depends on whether the form is about to be saved or just validated
during filling. If it is about to be saved, the minimum length requirement should be 
enforced (set second parameter to True). If the user will continue to draft the form 
(second parameter set to False) then the minimum length requirement shall only be 
enforced if the user has already written something. This is useful to avoid displaying 
an error message although the user may have skipped the text field intentionally for 
now. If minimum length shall always be enforced, just omit the second parameter.

### Server-Side Validation
When receiving data from the client, validation should also be performed on the 
server-side as well. This is because the client can alter the code running on the
client's browser but not the code running on the server. Fortunately, you do not have
to write your validators again and can instead just reuse the ones you have already 
written for the client! It works like this:

Server-Side:
```py
# Import your text_length_validator from the above example here.

@anvil.server.callable
def save_text(text):
    text_length_validator.validate(text, True)
    # Do the actual saving here 
```

Client-Side:
```py
try:
    anvil.server.call("save_text", "My nice text.")
except ValidationError as e:
    e.translate()
    alert(str(e))
```
If validation fails, FluentAnvil will send the message id to the client. Just use
the `translate()` method of the exception, convert it to a string and display it 
somewhere as shown in the example above.

## Extras
### IETF Language Tag Registry
The IETF language tags are standardized. A list of all tags is available in the
[Language Subtag Registry](https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry)
which is provided by the [Internet Assigned Numbers Authority (IANA)](https://en.wikipedia.org/wiki/Internet_Assigned_Numbers_Authority).
It practically defines tags for all known languages (including almost extinct
ones). Fluent Anvil comes with preprocessed copy of this registry (excluding 
obsolete and duplicate tags). You can easily use it to create dropdowns that allow
your users to define a locale. For example, your users may upload a document and provide
the locale it is written in.

You can access this registry by using one of the following functions:
```py
from fluent_anvil.lib import fluent

# Returns a dictionary with language tags as keys and the name of the language as value.
# Example: 
# {
#   'soa': 'Thai Song', 
#   'adf': 'Dhofari Arabic', 
#   'atv': 'Northern Altai', 
#   'aqm': 'Atohwaim', 
#   ...
# }
fluent.get_language_options()

# Returns a dictionary with region tags as keys and the name of the region as value.
# Example: 
# {
#   '419': 'Latin America', 
#   'TL': 'Timor-Leste', 
#   'GD': 'Grenada', 
#   'SA': 'Saudi Arabia', 
#   'LU': 'Luxembourg', 
#   'ID': 'Indonesia', 
#   'PF': 'French Polynesia', 
#   ...
# }
fluent.get_region_options()

# Returns a dictionary with script tags as keys and the name of the script as value.
# Example: 
# {
#   'Glag': 'Glagolitic', 
#   'Loma': 'Loma', 
#   'Batk': 'Batak', 
#   'Avst': 'Avestan', 
#   'Khmr': 'Khmer',
#   ...
# }
fluent.get_script_options()
```

### Common Locale Data Repository
While IETF language tags are used to compose an arbitrary locale code (even nonsensical 
ones like "de-SA" for German as spoken in Saudi Arabia), the Common Locale Data 
Repository (CLDR) provides locale information like country names, month names, currency
names, currency formatting, etc. for real locale codes such as "yue-Hant" for 
Traditional Cantonese. You can obtain all possible locale options by using:

```py
from fluent_anvil.lib import fluent

# Returns a dictionary with locale codes as keys and the name of the locale as value.
# Example: 
# {
#   'en-MS': 'English (Montserrat)', 
#   'ksh': 'Colognian', 
#   'fr-CF': 'French (Central African Republic)', 
#   'wae': 'Walser', 
#   'pt-LU': 'Portuguese (Luxembourg)', 
#   'fr': 'French', 
#   'en-JE': 'English (Jersey)', 
#   ...
# }
fluent.get_locale_options()
```

You can also obtain possible currency options like this:
```py
from fluent_anvil.lib import fluent
# Returns a dictionary with currency tags as keys and the name of the currency as value.
# Example: 
# {
#   'IQD': 'Iraqi Dinar', 
#   'SDP': 'Sudanese Pound (1957–1998)', 
#   'ARL': 'Argentine Peso Ley (1970–1983)', 
#   'ESA': 'Spanish Peseta (A account)', 
#   'MAD': 'Moroccan Dirham', 
#   'AWG': 'Aruban Florin', 
#   'CHF': 'Swiss Franc', 
#   'GNF': 'Guinean Franc',
#   ...
# }
fluent.get_currency_options()
```

### General Remarks
All names returned by the `get_[something]_options()` (i.e., the dictionary values) are 
given in the selected locale or one of the selected fallback locales (as set by 
`fluent.set_locale()`) if the user's browser can translate them. If not,
the names are returned in English. If you would rather omit the name than bother
your users with an English translation, you can do so by setting the `translatable_only`
parameter of these functions to `True`.

All these functions also have a `style` parameter that can be set to one of the
following:
* fluent.STYLE_DIALECT_NARROW ; e.g. "Traditional Chinese (Hong Kong)"
* fluent.STYLE_DIALECT_SHORT 
* fluent.STYLE_DIALECT_LONG
* fluent.STYLE_STANDARD_NARROW ; e.g. "Chinese (Traditional, Hong Kong)"
* fluent.STYLE_STANDARD_SHORT
* fluent.STYLE_STANDARD_LONG

Note that not all styles lead to a different result for all subtags or locale codes. In
fact, the results are often the same for multiple styles. This is not a bug, because
how the styles are interpreted depends on the selected output locale (as set by 
`fluent.set_locale()`) as well as the locale code or subtag that shall be translated.

If you already have a subtag, locale code, or currency code, you can translate it into 
the locale selected by `fluent.set_locale()` like this:

```py
from fluent_anvil.lib import fluent

# Returns "American English"
fluent.get_locale_name("en-US")

# Returns "Germany"
fluent.get_region_name("DE")

# Returns "Latin"
fluent.get_script_name("Latn")

# Returns "Icelandic Króna"
fluent.get_currency_name("ISK")
```

The `style` parameter explained above is also available for all `get_[something]_name()` 
functions.

# Credits
FluentAnvil uses the following libraries:

* [fluent.js](https://github.com/projectfluent/fluent.js/): JavaScript implementation 
  of the Fluent localization framework.
* [Langcodes](https://github.com/rspeer/langcodes): A library for language codes. It
  is used for python-only locale matching.
* [get-user-locale](https://github.com/wojtekmaj/get-user-locale): A function that 
  returns the user's locale as an IETF language tag, based on all available sources. It 
  is used to determine the user's preferred languages.
