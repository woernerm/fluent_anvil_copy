import 'intl-pluralrules'
import { Localization, DOMLocalization } from "@fluent/dom";
import { FluentBundle, FluentResource } from "@fluent/bundle";
import { getUserLocales } from 'get-user-locale';
import {match} from '@formatjs/intl-localematcher'

/**
 * Load a fluent file for the given locale and url.
 * @param {string} locale - Locale as IETF language tag, e.g. "en-US".
 * @param {string} url - URL template to .ftl file.
 * @returns - Fluent resource.
 */
async function fetch_resource(locale, resourceId) {
    locale = locale.replace("-", "_") // Make Anvil-compatible path.
    const url = resourceId.replace("{locale}", locale);
    const response = await fetch(url);
    const text = await response.text();
    return new FluentResource(text);
}

  /**
   * Create fluent bundle for the given locale and resource id. Also returns a list
   * of all errors encountered.
   * @param {string} locale - Locale as IETF language tag, e.g. "en-US".
   * @param {string} urls - URL templates to .ftl files.
   * @param {object} errors - Container for all errors encountered during ftl parsing.
   * @returns {FluentBundle} - Fluent bundle.
   */
async function create_bundle(locale, urls, errors) {
    let bundle = new FluentBundle(locale);

    for (const url of urls) {
      let resource = await fetch_resource(locale, url);
      errors.entries += bundle.addResource(resource);
    }

    // Output errors, if any.
    for (const entry of errors.entries) {
      console.log("Error creating bundle for locale '" + locale + "':" + entry)
    }
    return bundle;
}

/**
 * Create a generator function for creating the desired fluent bundle and select a 
 * suitable fallback if necessary.
 * @param {string} locale - List of IETF language tags, e.g. "en-US" in order of 
 *    preference (with the first element being the most preferable).
 * @param {object} errors - Container for all errors encountered during ftl parsing.
 * @returns - Generator function for returning a fluent bundle.
 */
function create_bundle_generator(locales, errors){
    return async function* generate_bundles(urls) {
        let fallbacks = []
        yield await create_bundle(locales[0], urls, errors);
        if (locales.length > 1){
          fallbacks = locales.slice(1)
        }
      
        // Try the remaining (fallback) locale options.
        for (const entry of fallbacks) {
          yield await create_bundle(entry, urls, errors);
        }
    }
} 

/**
 * Tries to detect the user's preferred locale. Returns the given fallback locale if
 * the operation fails.
 * @param {string} fallback - Fallback locale as IETF language tag, e.g. "en-US". 
 * @returns {list} - Returns a list of preferred locales.
 */
export function get_user_locales(fallback){
  if (fallback){
    return getUserLocales({fallbackLocale: fallback, useFallbackLocale: true})
  }
  return getUserLocales()  
}

/**
 * Finds the best matching locales.
 * 
 * Given a list of requested locales and locales available (i.e. those supported by the 
 * application), the method returns an ordered list of available locales that best fit 
 * any of the requested locales. The first locale in the returned list is the one with
 * the best fit. If there is no sensible match, the fallback is returned (e.g. the 
 * application's primary / best supported language or a widely spoken locale like 
 * english).
 * 
 * @param {list} requested_locales - A list of locales that the user prefers.
 * @param {list} available_locales - A list of locales that the application supports.
 * @param {list} fallback - The locale to return if no sensible match is found.
 * @param {int} count - The maximum number of locales to return.
 * @returns {list} - The best fitting locale or the given default locale if there is
 * no sensible match.
 */
export function match_locale(requested_locales, available_locales, fallback, count=1){
  const opts = {algorithm: 'best fit'};
  let locales = []
  for(let i=0; i < available_locales.length && i < count; i++){
    let entry = match(requested_locales, available_locales.slice(i), fallback, opts)
    // Each locale should be returned only once.
    if (!locales.includes(entry)){
      locales.push(entry)
    }
  }
  return locales
}

/**
 * Interface to Intl.DisplayNames class. It is used to return the names of the given 
 * locales (e.g. "en-US", "US", "en", etc.), scripts, currencies, etc in the given 
 * locale. This is useful to create a translated language, currency or region selection.
 * 
 * @param {string} codes - List of identifiers to translate.
 * @param {string} locale - The locale to translate to.
 * @param {string} type - The type ("language", "region", "currency") to translate.
 * @param {string} style - The style ("long", "short", "narrow") to translate.
 * @param {string} language - The way of phrasing the translation e.g. British English 
 * or English (United Kingdom).
 * @returns {list} - Returns the translation of the given code in the given locale.
 */
export function get_display_name(codes, locales, type, language = "dialect", style = "long"){
  const opts = {type: type, style: style, languageDisplay: language, fallback: "none"};
  const translation = new Intl.DisplayNames(locales, opts);
  return codes.map(cd => translation.of(cd));
}

/**
 * Interface to Intl.DisplayNames class. It is used to return the names of the locales
 * that are supported on the client's machine, i.e. those for which there is a display
 * name available. If locales are given, a subset of this list is returned that is
 * supported.
 * 
 * @param {string} locales - List of locales to test for support. Null if all supported
 * locales shall be returned.
 * @returns {list} - Returns a list of all supported locales or a subset of the given
 * locales that are supported on the client's machine.
 */
export function get_supported_locales(locales){
  return Intl.DisplayNames.supportedLocalesOf(locales, {"localeMatcher": "lookup"})
}

/**
 * Initialize fluent translation system.
 * @param {string} urls - URL templates to the .ftl files. Use the
 * placeholder {locale} for inserting the desired locale. Since Anvil does not support
 * hypthens in directory names, the placeholder will use underscores, e.g. "en_US".
 * @param {string} locales - Locales as IETF language tag, e.g. "en-US" in the order
 * of preference (with the first element being the most preferable).
 * @returns {object} Object containing a fluent DOMLocalization and Localization
 * instance. In addition, it also contains containers for all errors encountered during
 * intialization of both instances.
 */
export function init_localization(urls, locales){
  let dom_errors = {entries: []}
  let main_errors = {entries: []}  
  
  const dom_bundle_gen = create_bundle_generator(locales, dom_errors)
  const loc_bundle_gen = create_bundle_generator(locales, main_errors)
    
    
  // Activate DOM localization
  const dom = new DOMLocalization(urls, dom_bundle_gen);
  dom.connectRoot(document.documentElement);
  dom.translateRoots(); 

  const main = new Localization(urls, loc_bundle_gen)

  return {
    dom: dom, 
    dom_errors: dom_errors.entries,
    main: main, 
    main_errors: main_errors.entries
  }
}

/**
 * Format the given date to a localized string.
 * @param {list} locales List of locales in order of preference.
 * @param {datetime} isostring The date and time
 * @param {object} options Object with special options.
 * @returns String with the localized date and time.
 */
export function format_date(locales, isostring, options = null){
  const datetime = new Date(isostring)
  return new Intl.DateTimeFormat(locales, options ?? {}).format(datetime);
}

/**
* Format the given date to a localized string.
* @param {list} locales List of locales in order of preference.
* @param {datetime} value The numeric value to format.
* @param {object} options Object with special options.
* @returns String with the localized date and time.
*/
export function format_number(locales, value, options = null){
 return new Intl.NumberFormat(locales, options ?? {}).format(value);
}