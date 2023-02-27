# Introduction
[Fluent](https://projectfluent.org/) is a localization system for natural-sounding translations. There are official implementations for [JavaScript](https://github.com/projectfluent/fluent.js), [Python](https://github.com/projectfluent/python-fluent) and [Rust](https://github.com/projectfluent/fluent-rs). This library provides an interface for [anvil.works](https://anvil.works/). It is intended to be used with the corresponding anvil app. The app comes with a built version so you do not need to download this library unless you want to contribute (you are welcome to do so) or want to know how it works.

# Why use Fluent?
In contrast to gettext you can create more nuanced and natural sounding translations. For example, Polish has more plural forms than English or German. Therefore, selecting the right translation requires knowing whether there are one, few or many of something. With localization systems like gettext, this requires adding additional logic inside your application for every special case you might encounter for all languages you want to support. With fluent, this language-specific logic is encapsulated in the translation file and does not impact other translations.

Personally, I also find fluent easier to learn and use than gettext. In simple cases, a translation for a given locale is just a text file with string definitions like:
```
close-button = Close
```
If you have simple translations, the file stays simple. If a translation happens to be more complicated for a language, you only have to add the logic in the translation file for that particular language.

You can find out more about fluent at [Project Fluent](https://projectfluent.org/).
