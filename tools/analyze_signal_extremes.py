from tools.lookup import lookup_signal  # 👈 Import the signal lookup tool

def analyze_signal_extremes(rag_context: dict, english_name: str, mode: str = "max") -> dict:
    
    lookup_result = lookup_signal(rag_context=rag_context, english_name=english_name)

    if not lookup_result or "data" not in lookup_result or not lookup_result["data"]:
        return {"result": "❌ Signal lookup failed or returned no data."}

    signal_data = lookup_result["data"]
    values = signal_data.get("values", [])
    timestamps = signal_data.get("timestamps", [])

    if not values or not timestamps:
        return {"result": "❌ Signal data is missing timestamps or values."}

    # Step 2: Compute extremes
    if mode == "max":
        extreme_val = max(values)
        idx = values.index(extreme_val)
    elif mode == "min":
        extreme_val = min(values)
        idx = values.index(extreme_val)
    else:
        return {"result": "❌ Invalid mode. Use 'max' or 'min'."}

    extreme_time = timestamps[idx] if idx < len(timestamps) else None

    return {
        "result": f"✅ {mode.title()} value of '{signal_data['name']}' is {extreme_val} at time {extreme_time}",
        "value": extreme_val,
        "timestamp": extreme_time,
        "signal": signal_data['name']
    }