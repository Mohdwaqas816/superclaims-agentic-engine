import json

def safe_parse_json(raw):
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        # attempt to extract a JSON substring
        import re
        m = re.search(r'(\{.*\})', raw, flags=re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except:
                return {}
    return {}
