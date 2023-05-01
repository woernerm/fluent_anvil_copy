# Fluent Anvil
This library makes it easy to serve high-quality translated and localized versions of your [Anvil](https://anvil.works/) app. You can make your app appeal to and accessible for everyone. All you need to do is add it as a third party dependency with the token UHLC7WE6TELL25TO . You do not need to download this repository unless you want to contribute (you are welcome to do so) or want to know how it works. 

The library serves as a Python interface to [Fluent](https://projectfluent.org/). It is a localization system developed by Mozilla for natural-sounding translations. In contrast to gettext you can create more nuanced and natural sounding translations. For example, Polish has more plural forms than English or German. Therefore, selecting the right translation requires knowing how many there are of something. With localization systems like gettext, this requires adding additional logic inside your application. With Fluent, this language-specific logic is encapsulated in the translation file and does not impact other translations.

Personally, I think the greatest thing about Fluent apart from the translation quality is that is easier to learn and use than gettext: It uses only one simple text file format (.ftl) and does not require specialized extraction tools. Often, translations are as simple as this:

en_US/main.ftl:
```
close-button = Close
```
de_DE/main.ftl:
```
close-button = Schließen
```

For simple translations, the syntax stays simple: Define a message id like `close-button` and provide the translation after the equal sign. If a 
translation happens to be more complicated for a language, you only need to add the logic in the translation file for that particular language. 
You can find out more at [Project Fluent](https://projectfluent.org/).
The translation happens entirely on the client side. Therefore, it works on [Anvil's free plan](https://anvil.works/pricing) as well since there is no need to install a special package.

Please note that this is a personal project with the hope that it may be of use to others as well. I am neither affiliated with [Project Fluent](https://projectfluent.org/) nor [Anvil](https://anvil.works/).

## Quick Guide
In Anvil's assets section, add a directory to place your translations in, ideally you have one subfolder for each locale, e.g.
- localization
     - es_MX
         - main.ftl
     - en_US
         - main.ftl
     - de_DE
         - main.ftl

With Fluent, you can use variables for placeholders or selecting the appropriate translation. In the following example we are going to greet the user. Therefore, we use a variable as a placeholder for the user's name. Assume that the content of es_MX/main.ftl is: 
`hello = Hola { $name }.`

Then, import the fluent singleton object and the Message class in your form (Message is optional but required for the examples):
```py
from fluent_anvil.lib import fluent, Message
```
If you want to know which locale the user prefers, just call
```py
fluent.get_preferred_locales()
```
This will return a list of locales such as `['de-DE']` that the user prefers (this method does not use Fluent but the [get-user-locale](https://www.npmjs.com/package/get-user-locale) package).

Now, you can configure Fluent using the following (we ignore the preferred locale for now):
```py
fluent.configure(["es-MX"], "localization/{locale}/main.ftl")
```
This will tell fluent to use the Mexican Spanish locale. The first parameter is a list of desired locales. Locales are given in the order of preference (most preferable first). This means, Fluent will always try the first locale in the list when trying to find a translation. If a translation is not available for that locale, Fluent will try the others one after another until a suitable translation has been found. The second parameter is a template string indicating where the translation files are stored. The placeholder {locale} is replaced with the desired locale (hyphens converted to underscore, because Anvil does not allow hyphens in directory names). Generally, all methods of the `fluent` Python object accept locales regardless of whether you use hyphens or underscores. Note that you do not have to provide the full URL starting with `./_/theme/`. It will be prepended automatically. If your translation files are stored somewhere else entirely you can explicitly set the prefix by adding it to the end of the parameter list. The template string in the above example is actually the default. So, if you store your translations files in the way outlined above, you can omitt it. In this case, the call becomes simply:
```py
fluent.configure(["es-MX"])
```

Now, you can greet the user:
```py
print(fluent.format("hello", name="John"))
```
Every variable you want to have access to in your .ftl files can be added as a keyword variable. Apart from facts like the user's name this can be used to determine a natural sounding translation. These variables may include the count of something or the time of day. Depending on the type of variable, Fluent will automatically format the value according to the selected locale. For example, these messages:
en_US/main.ftl:
`time-elapsed = Time elapsed: { $duration }s.`
and
de_DE/main.ftl:
`time-elapsed = Vergangene Zeit: { $duration }s.`
After calling a command like
```py
print(fluent.format("time-elapsed", duration=12342423.234 ))
```
the message will show up with locale `en-US` as:
`Time elapsed: ⁨12,342,423.234⁩s.`
While with locale "de_DE" it will show up as:
`Vergangene Zeit: ⁨12.342.423,234⁩s.`
Pay attention to the use of dot and comma which is specific to the respective countries.

You can translate multiple strings at once (that's more efficient than one by one) by wrapping them in Message objects:
```py
print(fluent.format(
    Message("hello", name="World"), 
    Message("welcome-back", name="John"),
    ...
))
```
This returns a list of all translations in the same order as the corresponding Message instances.

You can switch to a different locale on the fly using `set_locale()`. Again, the first list element is the desired locale and the remaining entries in the list are fallback locales in case the translation searched for is not available for the desired locale.
```py
fluent.set_locale(["en-US", "en-GB", "en-AU"])
```
Although this is completely equivalent to `fluent.configure(["en-US", "en-GB", "en-AU"])`, its meaning is more obvious when reading code.

### Keeping Translation Code Short and Expressive
You often have various data structures that require translation. These include
Anvil component attributes, lists, dictionaries and combinations of these. With Fluent-Anvil
you can translate them on the fly without the need to unpack, translate and repack them again.
Some examples are given in the following.

#### Dictionaries
The format() method also works with dictionaries for which it will translate the values:
```py
fluent.format({
        "my key 1": "my-fluent-message",
        "my key 2": "my-other-fluent-message"
    })
```

#### Anvil Components
One of my favorite features is the possibility to write directly to GUI component attributes:
```py
fluent.format(
    Message("hello", name="world"), 
    Message(self.label, "text", "hello", name="John"),
)
```
You just provide the component and the name of the attribute you want to write to (similar to Python's `setattr()` function).

#### Lists of Dictionaries (Anvil Extras MultiSelectDropdown)
Lists of dictionaries are commonly used to model tables: The list entries represent rows 
and each dictionary entry represents a named column. You can translate these using the `format_table()` method. In the following
example we are going to translate the names of time units. The data structure is typical to what the
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
The second parameter is a list of keys to translate. Fluent-Anvil assumes that the value of every given key
represents a Fluent message id. Other keys and their values will not be touched and returned as-is.
Context variables can be provided as keyworded arguments or omitted completely. For example,
consider you selected "de_DE" as locale and had someone provide you with the corresponding .ftl
file, the result might look like this:

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
You can translate your static content as well. Just add the tags `data-l10n-id` for the message id and `data-l10n-args` for context variables (if needed) like this:
```html
<h1 id='welcome' data-l10n-id='hello' data-l10n-args='{"name": "world"}'>Localize me!</h1>
```
If you do not initialize a Fluent instance, you will see "Localize me!". As soon as the Fluent instance is initialized (e.g. with locale es-MX), the text changes to "Hola ⁨world⁩". If Fluent would fail for some reason, the default text (in this case "Localize me!") would be shown.

## Validation
An essential part of a good user interface is proper input validation. This requires
that you provide feedback to the user in a language the user understands. Fluent-Anvil
has you covered there as well: The validator module defines a `Validator` class with
which you can define a translated validation procedure. 

Consider a datepicker called `my_datepicker` that allows the user to define a deadline for a task. We want to 
validate that the selected date is not in the past. Otherwise, a message informing
the user about the invalid date shall be shown using a label component called 
`my_label`. A solution might look like this:

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
* A function that returns True, if the value to be validated passed the validation test. False, otherwise. Alternatively,
it may also be a [Zod validator from Anvil Extras](https://anvil-extras.readthedocs.io/en/latest/guides/modules/zod.html).
* A Fluent message id that represents an explainatory message to the user if validation fails.

In the Form class of the Anvil app, we can define a change event for the datepicker in which validation
is performed:

```py
from fluent_anvil.lib import ValidationError

# Some other code

def my_datepicker_change(self, **event_args):
    try:
        deadline_validator.validate(self.my_deadline.value)
        self.my_label.text = ""
    except ValidationError as error:
        self.my_label.text = str(error)
```
The `validate(value, *args, **kwargs)` method calls the lambda function defined earlier
when creating the Validator instance in the previous example. You are not limited to a 
single parameter. You can define an arbitrary validation function signature as long as 
it has at least one required parameter. You then provide all required parameter values to 
`validate(value, *args, **kwargs)`. If validation passes, nothing happes. In the above
example, the label text is set to an empty string. If validation fails, a ValidationError
is thrown. The exception message will contain the desired translation defined earlier.

Multiple validation steps can be combined during initialization by alternately providing
validation function and Fluent message id like this:
```py
from fluent_anvil.lib import Validator

text_length_validator = Validator(
    lambda text: len(text) > 10,
    "text-too-short",
    lambda text: len(text) < 120,
    "text-too-long",
    my_context_var = "my context
)
```
When calling `validate(value, *args, **kwargs)`, the validation functions are called
one after another. In the above example, it is first checked whether the text is long
enough. After that, it is checked whether the text is short enough. As usual, context
variables that are passed on to Fluent can be provided as keyworded arguments or omitted 
completely.

Validator objects are callable. This is useful, if you do not want to throw an exception:
```py
from fluent_anvil.lib import ValidationError

# Some other code

def my_datepicker_change(self, **event_args):
    self.my_label.text = deadline_validator(self.my_deadline.value, "")
```
If the provided value passes validation, the given default value is returned (usually 
an empty string, None or some other special value). Otherwise, the translated error 
message is returned.

So, should you use `my_validator.validate(value, *args, **kwargs)` or 
`my_validator(value, default, *args, **kwargs)`? This depends on what you want to do
in case validation fails. If you just want to display a message, just call the
validator. If you want to do several things at once like showing the message and
changing the role of a component (e.g. to highlight the text box for which
validation failed), use `my_validator.validate(value, *args, **kwargs)` in a 
try...except block as shown in the first example.