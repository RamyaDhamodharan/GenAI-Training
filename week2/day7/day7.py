import os
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

from dotenv import load_dotenv
from openai import OpenAI
from pymongo import MongoClient


# ============================================================
# 1. ENVIRONMENT
# ============================================================

CURRENT_DIR = Path(__file__).resolve().parent
ENV_PATH = Path("C:/Users/User/Desktop/GenAI-Training/.env")

load_dotenv(ENV_PATH)


API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise RuntimeError(
        f"OPENROUTER_API_KEY not found.\n"
        f"Expected .env file at:\n{ENV_PATH}"
    )


# ============================================================
# 2. OPENROUTER CLIENT
# ============================================================

client = OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


# ============================================================
# 3. MODELS
# ============================================================

PRIMARY_MODEL = "openai/gpt-4o-mini"
FALLBACK_MODEL = "openai/gpt-4o-mini"


# ============================================================
# 4. PRICES
#
# Prices are USD per 1 million tokens.
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
# 5. MONGODB CONNECTION
# ============================================================

MONGO_URI = "mongodb://127.0.0.1:27017/"

mongo_client = MongoClient(MONGO_URI)

# Test MongoDB connection
mongo_client.admin.command("ping")

print("✓ MongoDB connected successfully.")


# Database
db = mongo_client["genai_training"]


# Collection
conversations_collection = db["conversations"]


# Unique ID for this conversation
conversation_id = str(uuid4())


# ============================================================
# 6. CONVERSATION HISTORY
# ============================================================

SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are a helpful AI assistant. "
        "Answer clearly and concisely."
    ),
}


history = [
    SYSTEM_MESSAGE
]


# ============================================================
# 7. CREATE INITIAL CONVERSATION IN MONGODB
# ============================================================

conversations_collection.insert_one(
    {
        "conversation_id": conversation_id,

        "created_at": datetime.now(timezone.utc),

        "updated_at": datetime.now(timezone.utc),

        "messages": [
            {
                "role": "system",
                "content": SYSTEM_MESSAGE["content"],
            }
        ],

        "total_input_tokens": 0,

        "total_output_tokens": 0,

        "total_cost": 0.0,
    }
)


print(f"✓ Conversation created: {conversation_id}")


# ============================================================
# 8. RUNNING COST
# ============================================================

total_cost = 0.0


# ============================================================
# 9. TOKEN / COST CALCULATION
# ============================================================

def calculate_cost(model, input_tokens, output_tokens):
    """
    Calculate cost for one API request.
    """

    price = PRICING[model]

    input_cost = (
        input_tokens / 1_000_000
    ) * price["input"]

    output_cost = (
        output_tokens / 1_000_000
    ) * price["output"]

    return input_cost + output_cost


# ============================================================
# 10. CALL MODEL WITH STREAMING
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
        # TEXT
        # ----------------------------------------------------

        if chunk.choices:

            delta = chunk.choices[0].delta

            if delta.content:
                print(
                    delta.content,
                    end="",
                    flush=True
                )

                response_text += delta.content

        # ----------------------------------------------------
        # USAGE
        # ----------------------------------------------------

        if chunk.usage:

            input_tokens = chunk.usage.prompt_tokens

            output_tokens = chunk.usage.completion_tokens

    print()

    print("-" * 60)

    return (
        response_text,
        input_tokens,
        output_tokens,
    )


# ============================================================
# 11. SAVE TURN TO MONGODB
# ============================================================

def save_turn_to_mongodb(
    user_input,
    response_text,
    used_model,
    input_tokens,
    output_tokens,
    turn_cost,
):
    """
    Saves one successful conversation turn to MongoDB.
    """

    conversations_collection.update_one(
        {
            "conversation_id": conversation_id
        },

        {
            "$push": {
                "messages": {
                    "$each": [
                        {
                            "role": "user",
                            "content": user_input,
                            "timestamp": datetime.now(
                                timezone.utc
                            ),
                        },
                        {
                            "role": "assistant",
                            "content": response_text,
                            "timestamp": datetime.now(
                                timezone.utc
                            ),
                        },
                    ]
                }
            },

            "$inc": {
                "total_input_tokens": input_tokens,

                "total_output_tokens": output_tokens,

                "total_cost": turn_cost,
            },

            "$set": {
                "updated_at": datetime.now(
                    timezone.utc
                ),

                "last_model": used_model,
            },
        },
    )


# ============================================================
# 12. MAIN CONVERSATION
# ============================================================

def main():

    global total_cost

    print("=" * 60)

    print(
        "        MULTI-TURN LLM CONVERSATION"
    )

    print("=" * 60)

    print(
        f"Primary model : {PRIMARY_MODEL}"
    )

    print(
        f"Fallback model: {FALLBACK_MODEL}"
    )

    print(
        f"Conversation ID: {conversation_id}"
    )

    print("\nCommands:")

    print(
        "  exit  -> stop conversation"
    )

    print(
        "  break -> intentionally break primary model"
    )

    print()

    # --------------------------------------------------------
    # PRIMARY MODEL
    # --------------------------------------------------------

    primary_model = PRIMARY_MODEL


    # ========================================================
    # CONVERSATION LOOP
    # ========================================================

    while True:

        try:

            user_input = input("You: ").strip()

        except (KeyboardInterrupt, EOFError):

            print("\nExiting...")

            break


        # ----------------------------------------------------
        # EMPTY INPUT
        # ----------------------------------------------------

        if not user_input:

            continue


        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if user_input.lower() == "exit":

            print(
                "\nConversation ended."
            )

            break


        # ----------------------------------------------------
        # INTENTIONALLY BREAK PRIMARY MODEL
        # ----------------------------------------------------

        if user_input.lower() == "break":

            primary_model = (
                "this-model-does-not-exist"
            )

            print(
                "\n⚠️ Primary model intentionally broken."
            )

            print(
                f"Primary model is now: "
                f"{primary_model}"
            )

            print(
                "Next request will automatically "
                "use fallback."
            )

            continue


        # ----------------------------------------------------
        # ADD USER MESSAGE TO TEMPORARY HISTORY
        # ----------------------------------------------------

        history.append(
            {
                "role": "user",
                "content": user_input,
            }
        )


        # ====================================================
        # DEFAULT VALUES
        # ====================================================

        used_model = None

        response_text = ""

        input_tokens = 0

        output_tokens = 0


        # ====================================================
        # TRY PRIMARY MODEL
        # ====================================================

        try:

            print(
                "\nTrying primary model..."
            )


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

            print(
                "\n⚠️ Primary model failed."
            )

            print(
                "Switching to fallback model..."
            )


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
                    f"✓ Fallback successful: "
                    f"{FALLBACK_MODEL}"
                )


            # =================================================
            # BOTH MODELS FAILED
            # =================================================

            except Exception as fallback_error:

                print(
                    "\n❌ Both models failed."
                )

                print(
                    f"Primary error: "
                    f"{primary_error}"
                )

                print(
                    f"Fallback error: "
                    f"{fallback_error}"
                )


                # --------------------------------------------
                # Remove user message from temporary history
                # because no response was generated.
                # --------------------------------------------

                history.pop()

                continue


        # ====================================================
        # SAVE ASSISTANT RESPONSE TO TEMPORARY HISTORY
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
        # SAVE SUCCESSFUL TURN TO MONGODB
        # ====================================================

        save_turn_to_mongodb(
            user_input=user_input,

            response_text=response_text,

            used_model=used_model,

            input_tokens=input_tokens,

            output_tokens=output_tokens,

            turn_cost=turn_cost,
        )


        print(
            "\n✓ Conversation saved to MongoDB."
        )


        # ====================================================
        # PRINT TOKEN INFORMATION
        # ====================================================

        print("\n📊 Usage")

        print(
            f"Model          : {used_model}"
        )

        print(
            f"Input tokens   : {input_tokens}"
        )

        print(
            f"Output tokens  : {output_tokens}"
        )

        print(
            f"Turn cost      : ${turn_cost:.8f}"
        )

        print(
            f"Total cost     : ${total_cost:.8f}"
        )

        print(
            f"History msgs   : {len(history)}"
        )

        print(
            f"Conversation ID: {conversation_id}"
        )

        print("=" * 60)


# ============================================================
# 13. PYTHON ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        main()

    finally:

        # Close MongoDB connection
        mongo_client.close()

        print(
            "\n✓ MongoDB connection closed."
        )