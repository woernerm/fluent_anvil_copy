import { Localization, DOMLocalization } from "@fluent/dom";
import { FluentBundle, FluentResource } from "@fluent/bundle";
import { getUserLocales } from 'get-user-locale';

/**
 * Load a fluent file for the given locale and url.
 * @param {string} locale - Locale as IETF language tag, e.g. "en-US".
 * @param {string} resourceId - URL template to .ftl file.
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
   * @param {string} resourceId - URL template to .ftl file.
   * @param {object} errors - Container for all errors encountered during ftl parsing.
   * @returns {FluentBundle} - Fluent bundle.
   */
async function create_bundle(locale, resourceId, errors) {
    let resource = await fetch_resource(locale, resourceId);
    let bundle = new FluentBundle(locale);
    errors.entries += bundle.addResource(resource);

    // Output errors, if any.
    for (const entry of errors.entries) {
      console.log("Error creating bundle for locale " + locale + entry)
    }
    return bundle;
}

/**
 * Create a generator function for creating the desired fluent bundle and select a 
 * suitable fallback if necessary.
 * @param {string} locale - Locale as IETF language tag, e.g. "en-US". 
 * @param {list} fallback_locales - Fallback locales as lift of IETF language tags.
 * @param {object} errors - Container for all errors encountered during ftl parsing.
 * @returns - Generator function for returning a fluent bundle.
 */
function create_bundle_generator(locale, fallback_locales, errors){
    return async function* generate_bundles(resourceIds) {
        yield await create_bundle(locale, resourceIds[0], errors);
      
        for (const entry of fallback_locales) {
          yield await create_bundle(entry, resourceIds[0], errors);
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
 * @param {string} resource_path_template - URL template to the .ftl files. Use the
 * placeholder {locale} for inserting the desired locale. Since Anvil does not support
 * hypthens in directory names, the placeholder will use underscores, e.g. "en_US".
 * @param {string} locale - Locale as IETF language tag, e.g. "en-US". 
 * @param {list} fallback_locales - Fallback locale as IETF language tag, e.g. "en-US". 
 * @returns {object} Object containing a fluent DOMLocalization and Localization
 * instance. In addition, it also contains containers for all errors encountered during
 * intialization of both instances.
 */
export function init_localization(resource_path_template, locale, fallback_locales){
  let dom_errors = {entries: []}
  let main_errors = {entries: []}  
  
  const dom_bundle_gen = create_bundle_generator(locale, fallback_locales, dom_errors)
  const loc_bundle_gen = create_bundle_generator(locale, fallback_locales, main_errors)
    
    
  // Activate DOM localization
  const dom = new DOMLocalization(
      [resource_path_template], 
      dom_bundle_gen
  );
  dom.connectRoot(document.documentElement);
  dom.translateRoots(); 

  const main = new Localization([resource_path_template], loc_bundle_gen)

  return {
    dom: dom, 
    dom_errors: dom_errors.entries,
    main: main, 
    main_errors: main_errors.entries
  }
}