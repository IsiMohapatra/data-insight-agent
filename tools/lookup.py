import difflib

def lookup_signal(english_name: str, rag_context: dict):
    print(f"🔍 Looking up signal for: {english_name}")

    # Normalize input
    normalized_input = english_name.replace("_", " ").lower()

    # Build a list of all available user_names (normalized)
    mapping_list = rag_context.get("excel", {}).get("engish-inca mapping", [])
    user_names = [m["user_name"] for m in mapping_list]
    normalized_names = [name.replace("_", " ").lower() for name in user_names]

    # Try exact match first
    if normalized_input in normalized_names:
        idx = normalized_names.index(normalized_input)
        inca_name = mapping_list[idx]["inca_name"]
    else:
        # Fuzzy match: find the closest match
        close_matches = difflib.get_close_matches(normalized_input, normalized_names, n=1, cutoff=0.7)
        if close_matches:
            idx = normalized_names.index(close_matches[0])
            inca_name = mapping_list[idx]["inca_name"]
            print(f"🔎 Fuzzy matched '{english_name}' to '{mapping_list[idx]['user_name']}'")
        else:
            return {
                "result": f"❌ Not Found: English name '{english_name}' not mapped to INCA name.",
                "data": None
            }

    # Check MF4 signals
    mf4_signals = rag_context.get("mf4", [])
    for signal in mf4_signals:
        if signal.get("name") == inca_name:
            return {
                "result": f"✅ Found: {inca_name}",
                "data": {
                    "name": inca_name,
                    "timestamps": signal.get("timestamps", []),
                    "values": signal.get("values", [])
                }
            }

    return {
        "result": f"❌ Not Found in MF4: {inca_name}",
        "data": None
    }