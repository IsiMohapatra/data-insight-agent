# tools/plot_signals.py

import matplotlib.pyplot as plt
from tools.lookup import lookup_signal

def plot_signal(signal1_name: str, rag_context: dict, signal2_name: str = None) -> dict:
    print(f"📈 Plotting: {signal1_name}" + (f" vs {signal2_name}" if signal2_name else ""))

    # Lookup signal 1
    s1_result = lookup_signal(rag_context=rag_context, english_name=signal1_name)
    if not s1_result["data"]:
        return {"result": f"❌ Signal not found: {signal1_name}"}
    s1_data = s1_result["data"]
    s1_values = s1_data.get("values", [])
    s1_timestamps = s1_data.get("timestamps", [])

    # If signal 2 is not provided, plot signal 1 over time
    if not signal2_name:
        plt.figure(figsize=(10, 5))
        plt.plot(s1_timestamps, s1_values, label=signal1_name, color='blue')
        plt.xlabel("Time (s)")
        plt.ylabel("Value")
        plt.title(f"{signal1_name} over Time")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()
        return {"result": f"✅ Plotted '{signal1_name}' over time."}

    # Lookup signal 2
    s2_result = lookup_signal(rag_context=rag_context, english_name=signal2_name)
    if not s2_result["data"]:
        return {"result": f"❌ Signal not found: {signal2_name}"}
    s2_data = s2_result["data"]
    s2_values = s2_data.get("values", [])
    s2_timestamps = s2_data.get("timestamps", [])

    # Align both signals to the same length
    min_len = min(len(s1_values), len(s2_values))
    s1_values = s1_values[:min_len]
    s2_values = s2_values[:min_len]
    s1_timestamps = s1_timestamps[:min_len]
    s2_timestamps = s2_timestamps[:min_len]

    # Plot signal2 vs signal1
    plt.figure(figsize=(10, 5))
    plt.plot(s1_values, s2_values, label=f'{signal2_name} vs {signal1_name}', color='purple')
    plt.xlabel(f"{signal1_name} (X)")
    plt.ylabel(f"{signal2_name} (Y)")
    plt.title(f"{signal2_name} vs {signal1_name}")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    return {"result": f"✅ Plotted '{signal1_name}' and '{signal2_name}'"}
