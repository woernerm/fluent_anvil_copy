import {match} from '@formatjs/intl-localematcher'

export function localematch(desired, supported, fallback){
    let matches = [];
    for(let i=0; i < Math.min(supported.length, desired.length); i++){
        let e = match(desired[i], supported, fallback, {algorithm: 'best fit'});
        if (!matches.includes(e)){matches.push(e);}
    }
    return matches;
}