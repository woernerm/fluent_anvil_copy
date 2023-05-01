hello = Hallo {$name}!
time-elapsed = Time elapsed: { $duration }s.

emails =
    { $unreadEmails ->
        [one] Du hast eine neue, ungelesene Mail.
       *[other] Du hast { $unreadEmails } ungelesene eMails.
    }

text-too-long = Es sind maximal {$max} Zeichen erlaubt.
text-too-short = Es müssen mehr als {$min} Zeichen eingegeben werden.
no-valid-mail = Bei {$value} handelt es sich nicht um eine korrekte eMail-Adresse.
