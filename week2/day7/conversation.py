import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


CURRENT_DIR = Path(__file__).resolve().parent
ENV_PATH = Path("C:/Users/User/Desktop/GenAI-Training/.env")

load_dotenv(ENV_PATH)


API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise RuntimeError(
        f"OPENROUTER_API_KEY not found.\n"
        f"Expected .env file at:\n{ENV_PATH}"
    )


client = OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


PRIMARY_MODEL = "openai/gpt-4.1-mini"
FALLBACK_MODEL = "openai/gpt-4o-mini"


# ============================================================
# 5. PRICES
#
# Prices are USD per 1 million tokens.
# Update these if your provider's current pricing changes.
# ============================================================

PRICING = {
    PRIMARY_MODEL: {
        "input": 0.40,
        "output": 1.60,
    },
    FALLBACK_MODEL: {
        "input": 0.15,
        "output": 0.60,
    },
}


# ============================================================
# 6. CONVERSATION HISTORY
# ============================================================

history = [
    {
        "role": "system",
        "content": (
            "You are a helpful AI assistant. "
            "Answer clearly and concisely."
        ),
    }
]


# ============================================================
# 7. RUNNING COST
# ============================================================

total_cost = 0.0


# ============================================================
# 8. TOKEN/COST CALCULATION
# ============================================================

def calculate_cost(model, input_tokens, output_tokens):
    """
    Calculate cost for one API request.
    """

    price = PRICING[model]

    input_cost = (input_tokens / 1_000_000) * price["input"]
    output_cost = (output_tokens / 1_000_000) * price["output"]

    return input_cost + output_cost


# ============================================================
# 9. CALL MODEL WITH STREAMING
# ============================================================

def call_model(model, messages):
    """
    Sends the complete conversation history to the model.

    Returns:
        response_text
        input_tokens
        output_tokens
    """

    response_text = ""

    print(f"\n[{model}]")
    print("-" * 60)

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        stream_options={
            "include_usage": True
        },
    )

    input_tokens = 0
    output_tokens = 0

    for chunk in stream:

        # ----------------------------------------------------
        # TEXT TOKEN
        # ----------------------------------------------------

        if chunk.choices:

            delta = chunk.choices[0].delta

            if delta.content:
                print(delta.content, end="", flush=True)
                response_text += delta.content

        # ----------------------------------------------------
        # USAGE
        # ----------------------------------------------------

        if chunk.usage:

            input_tokens = chunk.usage.prompt_tokens
            output_tokens = chunk.usage.completion_tokens

    print()
    print("-" * 60)

    return response_text, input_tokens, output_tokens


# ============================================================
# 10. MAIN CONVERSATION
# ============================================================

def main():

    global total_cost

    print("=" * 60)
    print("        MULTI-TURN LLM CONVERSATION")
    print("=" * 60)

    print(f"Primary model : {PRIMARY_MODEL}")
    print(f"Fallback model: {FALLBACK_MODEL}")

    print("\nCommands:")
    print("  exit  -> stop conversation")
    print("  break -> intentionally break primary model")
    print()

    # --------------------------------------------------------
    # DELIBERATELY BREAK PRIMARY MODEL
    # --------------------------------------------------------

    primary_model = PRIMARY_MODEL

    while True:

        try:

            user_input = input("You: ").strip()

        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if not user_input:
            continue

        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if user_input.lower() == "exit":
            print("\nConversation ended.")
            break

        # ----------------------------------------------------
        # INTENTIONALLY BREAK PRIMARY MODEL
        # ----------------------------------------------------

        if user_input.lower() == "break":

            primary_model = "this-model-does-not-exist"

            print("\n⚠️ Primary model intentionally broken.")
            print(
                f"Primary model is now: {primary_model}"
            )
            print(
                "Next request will automatically use fallback."
            )

            continue

        # ----------------------------------------------------
        # ADD USER MESSAGE TO HISTORY
        # ----------------------------------------------------

        history.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        # ====================================================
        # TRY PRIMARY MODEL
        # ====================================================

        used_model = None
        response_text = ""
        input_tokens = 0
        output_tokens = 0

        try:

            print("\nTrying primary model...")

            (
                response_text,
                input_tokens,
                output_tokens,
            ) = call_model(
                primary_model,
                history,
            )

            used_model = primary_model

        # ====================================================
        # PRIMARY FAILED → FALLBACK
        # ====================================================

        except Exception as primary_error:

            print("\n⚠️ Primary model failed.")
            print("Switching to fallback model...")

            try:

                (
                    response_text,
                    input_tokens,
                    output_tokens,
                ) = call_model(
                    FALLBACK_MODEL,
                    history,
                )

                used_model = FALLBACK_MODEL

                print(
                    f"✓ Fallback successful: {FALLBACK_MODEL}"
                )

            except Exception as fallback_error:

                # --------------------------------------------
                # BOTH MODELS FAILED
                # --------------------------------------------

                print("\n❌ Both models failed.")

                print(f"Primary error: {primary_error}")
                print(f"Fallback error: {fallback_error}")

                # Remove user message because no answer
                # was successfully generated.
                history.pop()

                continue

        # ====================================================
        # SAVE ASSISTANT RESPONSE TO HISTORY
        # ====================================================

        history.append(
            {
                "role": "assistant",
                "content": response_text,
            }
        )

        # ====================================================
        # CALCULATE CURRENT TURN COST
        # ====================================================

        turn_cost = calculate_cost(
            used_model,
            input_tokens,
            output_tokens,
        )

        total_cost += turn_cost

        # ====================================================
        # PRINT TOKEN INFORMATION
        # ====================================================

        print("\n📊 Usage")
        print(f"Model          : {used_model}")
        print(f"Input tokens   : {input_tokens}")
        print(f"Output tokens  : {output_tokens}")
        print(f"Turn cost      : ${turn_cost:.8f}")
        print(f"Total cost     : ${total_cost:.8f}")
        print(f"History msgs   : {len(history)}")

        print("=" * 60)


# ============================================================
# 11. PYTHON ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()