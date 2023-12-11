import { DOMLocalization } from "@fluent/dom";
import { FluentBundle, FluentResource } from "@fluent/bundle";
import { getUserLocales } from 'get-user-locale';
import {match} from '@formatjs/intl-localematcher'

/**
 * Dynamicaly import pluralrules polyfill, if necessary
 */
async function init_plural_rules(){
    if (typeof Intl.PluralRules === 'undefined') {
        await import('intl-pluralrules');
    }
}

/**
 * Fetch the data from multiple url's simultaneously and return the text result.
 * 
 * @param {Array} urls Array of urls to fetch.  
 * @returns Array with text contents for each url. Entries that failed will be null.
 */
export async function bulk_fetch(urls){
    const promises = urls.map(url => fetch(url));
    await Promise.all(promises);    
    let responses = [];
    for (let i = 0; i<promises.length; i++){
        let resp = await promises[i];
        if (resp.status == 200){
            responses.push(await resp.text());
        }else{
            console.warn("Unable to load " + urls[i] + ".");
        }
    }
    return responses;
}

class Locale{
    constructor(available, fallback, templates){
        this.available = available; // The locales available.
        this.fallback = fallback;
        this._selected = []; // Best matching available locales likely preferred.
        this.templates = templates; // URL templates to the .ftl files.
    }

    /**
     * Finds the best matching available locales with respect to the requested ones.
     * 
     * Given a list of requested locales, the method returns an ordered list of 
     * available locales that best fit any of the requested locales (best to worst fit).
     * 
     * @param {Array} requested - A list of locales that the user prefers.
     * @returns {Array} - The best fitting locales.
     */
    get selected(){
        if (!this._selected.length){
            const opts = {algorithm: 'best fit'};
            const usopts = {fallbackLocale: fb, useFallbackLocale: true};
            const fb = this.fallback;
            const requested = getUserLocales(usopts);
            
            for(let i=0; i < Math.min(this.available.length, requested.length); i++){
                let entry = match(requested, this.available.slice(i), fb, opts);
                if (!this._selected.includes(entry)){this._selected.push(entry);}
            }
        }
        if (!this._selected.length){console.error("Unable to select suitable locale.");}
        return this._selected
    }

    set selected(locales){
        this._selected = locales;
    }

    static async create(index_url, template_url, fallback){
        let [available, templates] = await bulk_fetch([index_url, template_url]);
        available = (available ?? "").split("\n").map((x) => x.replace("_", "-"));
        templates = (templates ?? "").split("\n");
        return new Locale(available, fallback, templates);
    }
}

class Fluent{
    /**
     * Create fluent bundle for the given locale and resource id. 
     * @param {string} loc - Locale as IETF language tag, e.g. "en-US".
     * @param {string} templates - URL templates to .ftl files.
     * @returns {FluentBundle} - Fluent bundle.
     */
    static async create_bundle(loc, templates) {
        let bundle = new FluentBundle(loc);
        const urls = templates.map((x) => x.replace("{locale}", loc.replace("-", "_"))); 

        for (const text of (await bulk_fetch(urls))){
          let errors = bundle.addResource(new FluentResource(text));
          for (const e of errors){console.error(e);}
        }
        return bundle;
    }

    /**
     * Create a fluent bundle generator.
     * @param {Locale} index - Locale object.
     * @returns - Generator function for returning a fluent bundle.
     */
    static create_bundle_generator(locale){
        return async function* generate_bundles(templates) {
            const locale_tags = (await locale).selected;   
            for (const loc of locale_tags){  
                yield await Fluent.create_bundle(loc, templates);
            }
        }
    } 

    /**
     * Initialize fluent translation system.
     * @param {string} index_url - The url to the index.lst file.
     * @param {string} template_url - The url to the templates.lst file.
     * @returns {object} Fluent instance.
     */
    constructor(index_url, template_url, fallback){
        this.locale = null;
        this.dom = null;

        this.initialized = new Promise(async (resolve, reject) => { 
            init_plural_rules();
            this.locale = await Locale.create(index_url, template_url, fallback);
            this.dom = new DOMLocalization(
                this.locale.templates, Fluent.create_bundle_generator(this.locale)
            );
            this.dom.connectRoot(document.documentElement);
            this.dom.translateRoots(); 
            resolve();
        }).then(() => {
            return true;
        });
    }

    /**
     * Interface to Intl.DisplayNames class. It is used to return the names of the given 
     * locales, scripts, currencies, etc.
     * 
     * @param {string} codes - List of identifiers to translate, e.g. "US".
     * @param {string} type - The type ("language", "region", "currency") to translate.
     * @param {string} style - The style ("long", "short", "narrow") to translate.
     * @param {string} language - The way of phrasing the translation e.g. British 
     *      English or English (United Kingdom).
     * @returns {string} - Returns the translation of the given code.
     */
    async get_display_name(fn, codes, type, language = "dialect", style = "long"){
        await this.initialized;
        const opts = {type: type, style: style, languageDisplay: language, fallback: "none"};
        const translation = new Intl.DisplayNames(this.index.selected, opts);
        const res = codes.map(cd => translation.of(cd));
        if (fn){fn(res);}
        return res;
    }

    /**
     * Format the given date to a localized string.
     * @param {datetime} isostr The date and time
     * @param {object} options Object with special options.
     * @returns String with the localized date and time.
     */
    async format_date(fn, isostr, options = null){
        await this.initialized;
        const res = new Intl.DateTimeFormat(this.locale.selected, options ?? {}).format(new Date(isostr));
        if (fn){fn(res);}
        return res;
    }

    /**
    * Format the given date to a localized string.
    * @param {datetime} value The numeric value to format.
    * @param {object} options Object with special options.
    * @returns String with the localized date and time.
    */
    async format_number(fn, value, options = null){
        await this.initialized;
        const res = new Intl.NumberFormat(this.locale.selected, options ?? {}).format(value);
        console.log("res: " + res)
        if (fn){fn(res);}
        console.log("return res:" + res)
        return res;
    }

    /**
    * Return the translations for the given keys.
    * @param {Array} keys List of message identifiers to translate.
    * @param {Function} fn Callback function to call once translations are ready.
    * @param {Array} args Arbitrary number of arguments passed to the callback function.
    * @returns Translations for the given keys.
    */
    async format_values(fn, keys, ...args){
        await this.initialized;
        let translations = await this.dom.formatValues(keys);
        translations = [...translations].map(t => t ?? null); // Coerce undefined to null.
        if (fn){fn(translations, ...args);}
    }
}

let fluent = new Fluent(
    "./_/theme/localization/index.lst", 
    "./_/theme/localization/templates.lst", 
    "en-US"
)

export {fluent};