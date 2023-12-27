import { expect, test, describe } from 'vitest'
import { localematch } from '../src/localematch.js'

describe('TestJSMatch', () => {
    test('return_the_best_matching_locale_for_a_single_requested_one', () => {
        const available = ["en-US", "en-GB"];
        expect(localematch(["en-US"], available, "en-US")).toEqual(["en-US"]);
        expect(localematch(["en-GB"], available, "en-US")).toEqual(["en-GB"]);
        expect(localematch(["en-CA"], available, "en-US")).toEqual(["en-GB"]);
    })

    test('return_requested_locale_if_it_is_part_of_the_available_ones', () => {
        const available = ["en-US", "en-GB", "en-CA"];
        expect(localematch(["en-US"], available, "en-US")).toEqual(["en-US"]);
        expect(localematch(["en-GB"], available, "en-US")).toEqual(["en-GB"]);
        expect(localematch(["en-CA"], available, "en-US")).toEqual(["en-CA"]);
    })

    test('return_a_list_of_best_matching_locales_for_multiple_requested_ones', () => {
        const available = ["en-US", "en-GB"];
        expect(localematch(["en-US", "en-GB"], available, "en-US")).toEqual(["en-US", "en-GB"]);
        expect(localematch(["en-GB", "en-US"], available, "en-US")).toEqual(["en-GB", "en-US"]);
        expect(localematch(["en-CA", "en-US"], available, "en-US")).toEqual(["en-GB", "en-US"]);
        expect(localematch(["en-CA", "en-GB"], available, "en-US")).toEqual(["en-GB"]);
    })

    test('return_the_fallback_locale_if_no_match_is_found', () => {
        expect(localematch(["am"], ["fr-FR", "de-DE"], "en-US")).toEqual(["en-US"]);
    })
})