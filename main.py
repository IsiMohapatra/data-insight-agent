import os
import json
import importlib
from dotenv import load_dotenv
from groq import Groq
from rag.context_builder import build_context_and_store

# 1. Load Environment
load_dotenv()

# 2. Get API Key and Initialize Groq client
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("❌ GROQ_API_KEY not found in environment variables.")

groq_client = Groq(api_key=groq_api_key)


def load_function_rules(rules_path="rag/manual.json"):
    if not os.path.exists(rules_path):
        raise FileNotFoundError(f"⚠️ manual.json not found at: {rules_path}")
    
    with open(rules_path, "r") as f:
        return json.load(f)

import traceback

def ask_llm_with_tools(user_prompt: str, rag_context: dict, rules_path="rag/manual.json"):
    # 🆕 LLM call to split the user prompt into sub-queries
    def split_into_queries(prompt):
        splitter_prompt = (
            "Split the following user prompt into individual task-based queries. "
            "Return a JSON list of each query. No explanation, no markdown.\n\n"
            f"Prompt: {prompt}\n\nOutput:"
        )
        try:
            response = groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a task splitter. You only return a JSON list of sub-queries."},
                    {"role": "user", "content": splitter_prompt}
                ]
            )
            queries = json.loads(response.choices[0].message.content.strip())
            if isinstance(queries, list):
                return queries
            else:
                return [prompt]  # fallback to whole prompt as one
        except Exception:
            traceback.print_exc()
            return [prompt]

    # 🆕 Split the user prompt first
    sub_queries = split_into_queries(user_prompt)

    print("\n📌 Split Queries:")
    for i, q in enumerate(sub_queries, 1):
        print(f"  {i}. {q}")

    function_rules = load_function_rules(rules_path)
    results = []

    for query in sub_queries:
        try:
            print(f"\n📡 Asking Groq to analyze sub-query: {query}")

            response = groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": (
                        "You are a helpful assistant for a CAN signal tool. "
                        "Analyze the user prompt and based on the context provided, "
                        "return the appropriate function to call. Strictly return only a JSON object like this — "
                        "no explanation, no markdown, no text — just the JSON:\n\n"
                        "{\n  \"function\": \"function_name\",\n  \"inputs\": { \"arg1\": value, ... }\n}"
                    )},
                    {"role": "user", "content": f"User prompt: {query}\n\nAvailable functions: {json.dumps(function_rules)}"}
                ]
            )

            model_reply = response.choices[0].message.content.strip()
            print("🧠 Raw LLM Response:", model_reply)

            try:
                parsed = json.loads(model_reply)
                function_name = parsed["function"]
                inputs = parsed["inputs"]
            except json.JSONDecodeError:
                print("💬 Fallback to friendly chat mode.")
                results.append({
                    "function": None,
                    "inputs": {},
                    "output": model_reply or "👋 Hello! How can I assist you today?"
                })
                continue

        except Exception as e:
            traceback.print_exc()
            results.append({
                "function": None,
                "inputs": {},
                "output": f"❌ Groq call failed: {str(e)}"
            })
            continue

        # Call the appropriate function (no changes here)
        try:
            module = importlib.import_module(f"tools.{function_name}")
            func = getattr(module, function_name)
            result = func(rag_context=rag_context, **inputs)

            results.append({
                "function": function_name,
                "inputs": inputs,
                "output": result
            })

        except Exception as e:
            traceback.print_exc()
            print(f"❌ Failed to call function `{function_name}`:", str(e))
            results.append({
                "function": function_name,
                "inputs": inputs,
                "output": f"❌ Error during function execution: {str(e)}"
            })

    return results


if __name__ == "__main__":
    import time

    excel_path = r"C:\Users\AFO3KOR\Desktop\english-inca mapping.xlsx"
    mf4_path = r"C:\Users\AFO3KOR\Desktop\Fleet Analysis\measurements\71878401511\20241017_1\20241017005907_71878401511_CANLogger_CC21_E20_Final_run_V3.mf4"

    print("⚙️  Initializing context from Excel and MF4 file...")
    rag_context = build_context_and_store(excel_path, mf4_path)
    print("✅ Context loaded successfully.\n")

    print("💬 You can now enter prompts (type 'exit' to quit).")

    while True:
        try:
            user_input = input("\n👤 Your prompt: ").strip()
            if user_input.lower() == "exit":
                print("👋 Exiting. Thank you!")
                break

            result = ask_llm_with_tools(user_input, rag_context)
            print(result)

        except KeyboardInterrupt:
            print("\n👋 Interrupted. Exiting.")
            break

        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
