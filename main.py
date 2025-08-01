import os
import json
import importlib
import traceback
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



def ask_llm_with_tools(user_prompt: str, rag_context: dict, rules_path="rag/manual.json"):
    system_prompt = (
        "You are a helpful assistant for a CAN signal tool. "
        "Analyze the user prompt and based on the context provided, "
        "return the appropriate function to call. Strictly return only a JSON object like this — "
        "no explanation, no markdown, no text — just the JSON:\n\n"
        "{\n  \"function\": \"function_name\",\n  \"inputs\": { \"arg1\": value, ... }\n}"
    )

    function_rules = load_function_rules(rules_path)

    try:
        print(f"Your prompt: {user_prompt}")
        print("📡 Asking Groq to analyze prompt...")

        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User prompt: {user_prompt}\n\nAvailable functions: {json.dumps(function_rules)}"}
            ]
        )
        
        model_reply = response.choices[0].message.content.strip()
        print("🧠 Raw LLM Response:", model_reply)

        try:
            parsed = json.loads(model_reply)
            function_name = parsed["function"]
            inputs = parsed["inputs"]
        except json.JSONDecodeError:
            # Fallback for small talk like "hello", "thanks", etc.
            print("💬 Fallback to friendly chat mode.")
            return {
                "function": None,
                "inputs": {},
                "output": model_reply or "👋 Hello! How can I assist you today?"
            }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "function": None,
            "inputs": {},
            "output": f"❌ Groq call failed: {str(e)}"
        }

    # Attempt to dynamically call the tool function
    try:
        module = importlib.import_module(f"tools.{function_name}")
        func = getattr(module, function_name)
        result = func(rag_context=rag_context, **inputs)

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Failed to call function {function_name}:", str(e))
        return {
            "function": function_name,
            "inputs": inputs,
            "output": f"❌ Error during function execution: {str(e)}"
        }

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
