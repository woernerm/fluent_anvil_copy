import { expect, test, describe } from 'vitest'
import { match } from '../src/locale.js'

describe('TestJSMatch', () => {
    test('return_the_best_matching_locale_for_a_single_requested_one', () => {
        const available = ["en-US", "en-GB"];
        expect(match(["en-US"], available, "en-US")).toEqual(["en-US"]);
        expect(match(["en-GB"], available, "en-US")).toEqual(["en-GB"]);
        expect(match(["en-CA"], available, "en-US")).toEqual(["en-GB"]);
    })

    test('return_requested_locale_if_it_is_part_of_the_available_ones', () => {
        const available = ["en-US", "en-GB", "en-CA"];
        expect(match(["en-US"], available, "en-US")).toEqual(["en-US"]);
        expect(match(["en-GB"], available, "en-US")).toEqual(["en-GB"]);
        expect(match(["en-CA"], available, "en-US")).toEqual(["en-CA"]);
    })

    test('return_a_list_of_best_matching_locales_for_multiple_requested_ones', () => {
        const available = ["en-US", "en-GB"];
        expect(match(["en-US", "en-GB"], available, "en-US")).toEqual(["en-US", "en-GB"]);
        expect(match(["en-GB", "en-US"], available, "en-US")).toEqual(["en-GB", "en-US"]);
        expect(match(["en-CA", "en-US"], available, "en-US")).toEqual(["en-GB", "en-US"]);
        expect(match(["en-CA", "en-GB"], available, "en-US")).toEqual(["en-GB"]);
    })

    test('return_the_fallback_locale_if_no_match_is_found', () => {
        expect(match(["am"], ["fr-FR", "de-DE"], "en-US")).toEqual(["en-US"]);
    })

    test('return_the_first_available_locale_if_no_fallback_is_given', () => {
        expect(match(["am"], ["fr-FR", "de-DE"])).toEqual(["fr-FR"]);
    })
})