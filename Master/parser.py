def parse_message(raw):
    """
    Parse les messages texte du type :
    KEY:VALUE
    KEY2:VALUE
    END
    """
    lines = raw.strip().split("\n")
    data = {}

    for line in lines:
        if line == "END":
            break
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()

    return data
