import {match as localematcher} from '@formatjs/intl-localematcher';
import { getUserLocales } from 'get-user-locale';

/**
 * Match locales using the browser's Intl API.
 * 
 * @param {*} desired List of requested locales (e.g. the ones the user prefers most)
 * @param {*} supported List of available locales.
 * @param {*} fallback Fallback locale that should be used if no match is found. If no
 *      fallback is given the first locale in the list of available ones is used. 
 */
export function match(desired, supported, fallback = null){
    let matches = [];
    for(let i=0; i < Math.min(supported.length, desired.length); i++){
        let e = localematcher(desired[i], supported, fallback, {algorithm: 'best fit'});
        if (!matches.includes(e)){matches.push(e);}
    }
    return matches.map(t => t ?? supported[0]);
}

export {match, getUserLocales};