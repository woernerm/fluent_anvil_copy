import anvil.server
def decompose(locale:str):
    loc = locale.replace("_", "-").strip().split("-")
    decomp = {}

    for i, entry in enumerate(loc):
        if i == 0:
            decomp["language"] = entry
        elif len(entry) == 3 and entry == entry.lower():
            decomp["extlang"] = entry
        elif len(entry) == 4 and entry == entry.title():
            decomp["script"] = entry
        elif (len(entry) == 2 and entry.isalpha()) or (len(entry) == 3 and entry.isnumeric()):
            decomp["region"] = entry
        elif len(entry) >= 4 and entry == entry.lower():
            decomp["variant"] = entry
        elif len(entry) == 1 and entry[0] == "u":
            decomp["extension"] = loc[i:]
        elif len(entry) == 1 and entry[0] == "x":
            decomp["privateuse"] = loc[i:]
        else:
            raise Exception(f'Cannot identify "{entry}" subtag in "{locale}".') 
    return decomp

def compose(pattern: dict, components: dict):
    def info(args: list):
        args = [e for e in args if e is not None]
        if len(args) > 1:
            pat = pattern["localeSeparator"]
            outp = pat.replace("{0}", args[0]).replace("{1}", info(args[1:]))
            return outp.strip()
        return "" if not args else args[0]

    extra = info([
        components.get("variant", None),
        components.get("script", None),
        components.get("region", None),
    ])
    
    if not extra:
        return components["language"]
    sep = pattern["localePattern"]
    return sep.replace("{0}", components["language"]).replace("{1}", extra)