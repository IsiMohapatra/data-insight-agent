import pandas as pd
import mdfreader
import json
import os
import numpy as np


def extract_excel_data(excel_path):
    """Read all sheets and store their data as dictionaries."""
    try:
        df_sheets = pd.read_excel(excel_path, sheet_name=None)
        excel_data = {}
        for sheet_name, df in df_sheets.items():
            excel_data[sheet_name] = df.fillna("NA").to_dict(orient="records")
        return excel_data
    except Exception as e:
        print(f"[!] Error reading Excel file: {e}")
        return {}

def extract_mf4_data(mf4_path):
    
    mdf_file = mdfreader.Mdf(mf4_path)
    all_signals = list(mdf_file.keys())
    signals = []
    
    for sig in all_signals:
        signal_data = np.array(mdf_file.get_channel_data(sig))
        master_channel = mdf_file.get_channel_master(sig)
        timestamps = np.array(mdf_file.get_channel_data(master_channel))

        signals.append({
            "name": sig,
            "timestamps": timestamps.tolist(),
            "values": signal_data.tolist()
        })

    return signals
    
        
def build_context_and_store(excel_path, mf4_path, save_path="rag/context_store.json"):
    """Combine Excel and MF4 extracted data and save as JSON."""

    # Create folder if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    context = {
        "excel": extract_excel_data(excel_path),
        "mf4": extract_mf4_data(mf4_path)
    }

    try:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(context, f, indent=2)
        print(f"[✓] Context stored at {save_path}")
    except Exception as e:
        print(f"[!] Error saving context JSON: {e}")

    return context
