import { expect, test } from 'vitest'
import { localematch } from '../src/localematch.js'

test('Return_the_best_matching_locale_for_a_single_requested_one', () => {
  expect(localematch(["en-US"], ["en-US", "en-GB"], "en-US")).toEqual(["en-US"])
})