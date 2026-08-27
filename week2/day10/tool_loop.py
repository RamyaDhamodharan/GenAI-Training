import os
import json

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# 1. ITERATION CAP
# ============================================================
# IMPORTANT:
# The cap is defined BEFORE the tool loop.
# This prevents the model-tool loop from running forever.

MAX_STEPS = 5


# ============================================================
# 2. OPENROUTER / OPENAI CLIENT SETUP
# ============================================================

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


# ============================================================
# 3. TOOL 1 — FETCH SOMETHING
# ============================================================

def fetch_course(course_id: str):
    """
    Fetch course information using a course ID.
    """

    courses = {
        "python101": {
            "name": "Python Basics",
            "price": 1000,
            "duration": "4 weeks"
        },
        "react101": {
            "name": "React Basics",
            "price": 1500,
            "duration": "5 weeks"
        }
    }

    return courses.get(
        course_id,
        {"error": "Course not found"}
    )


# ============================================================
# 4. TOOL 2 — CALCULATE SOMETHING
# ============================================================

def calculate_total(price: float, quantity: int):
    """
    Calculate total price using price and quantity.
    """

    return {
        "total": price * quantity
    }


# ============================================================
# 5. TOOL REGISTRY
# ============================================================
# The LLM gives us the tool name as text.
#
# Example:
#
#     "fetch_course"
#
# The registry converts that name into the actual
# Python function:
#
#     fetch_course
#
# This allows us to execute the tool dynamically.

TOOL_REGISTRY = {
    "fetch_course": fetch_course,
    "calculate_total": calculate_total
}


# ============================================================
# 6. TOOL SCHEMAS
# ============================================================
# These schemas tell the LLM:
#
# - What tools are available
# - What each tool does
# - When to use them
# - What arguments they require
#
# The LLM does NOT execute these functions.
# It only requests a tool call.

TOOLS = [

    {
        "type": "function",
        "function": {
            "name": "fetch_course",

            "description": (
                "Fetch course information using a course ID. "
                "Use this when the user asks for details about "
                "a specific course. "
                "Valid course IDs are python101 and react101. "
                "Returns the course name, price, and duration."
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "course_id": {
                        "type": "string"
                    }
                },

                "required": [
                    "course_id"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "calculate_total",

            "description": (
                "Calculate the total price using price and quantity. "
                "Use this when the user needs a multiplication "
                "calculation. "
                "Returns the total price."
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "price": {
                        "type": "number"
                    },

                    "quantity": {
                        "type": "integer"
                    }
                },

                "required": [
                    "price",
                    "quantity"
                ]
            }
        }
    }
]


# ============================================================
# 7. TOOL LOOP
# ============================================================

def run_tool_loop(
    user_input: str,
    max_steps: int = MAX_STEPS
):
    """
    Run the model-tool loop.

    Flow:

        User
          ↓
        LLM
          ↓
        Tool call?
          ↓
        Yes
          ↓
        Execute Python tool
          ↓
        Send result back to LLM
          ↓
        LLM again
          ↓
        Final answer

    The loop stops when:
        1. The model gives a final answer, OR
        2. MAX_STEPS is reached.
    """

    # --------------------------------------------------------
    # Conversation starts with the user's message.
    # --------------------------------------------------------

    messages = [
        {
            "role": "user",
            "content": user_input
        }
    ]

    # --------------------------------------------------------
    # HARD ITERATION CAP
    # --------------------------------------------------------
    # This prevents infinite tool loops.
    # The cap is intentionally written before the loop.

    for step in range(max_steps):

        print(f"\n========== STEP {step + 1} ==========")

        # ----------------------------------------------------
        # CALL THE MODEL
        # ----------------------------------------------------

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            tools=TOOLS,
            max_tokens=1000
        )

        assistant_message = response.choices[0].message

        # ----------------------------------------------------
        # CHECK WHETHER THE MODEL WANTS A TOOL
        # ----------------------------------------------------

        if not assistant_message.tool_calls:

            # No tool call means the model has finished.
            print("\n========== FINAL ANSWER ==========")
            print(assistant_message.content)

            return assistant_message.content

        # ----------------------------------------------------
        # MODEL REQUESTED A TOOL
        # ----------------------------------------------------

        print("\n========== TOOL CALL ==========")

        # Add the assistant's tool-call message
        # to the conversation history.

        messages.append(assistant_message)

        # ----------------------------------------------------
        # PROCESS EACH TOOL CALL
        # ----------------------------------------------------

        for tool_call in assistant_message.tool_calls:

            # Get the name of the requested tool.

            tool_name = tool_call.function.name

            # The arguments arrive as JSON text.
            # Convert JSON text into a Python dictionary.

            arguments = json.loads(
                tool_call.function.arguments
            )

            print("Tool:", tool_name)
            print("Arguments:", arguments)

            # ------------------------------------------------
            # FIND THE ACTUAL PYTHON FUNCTION
            # ------------------------------------------------

            tool_function = TOOL_REGISTRY.get(tool_name)

            if tool_function is None:

                result = {
                    "error": f"Unknown tool: {tool_name}"
                }

            else:

                # ------------------------------------------------
                # EXECUTE THE PYTHON TOOL
                # ------------------------------------------------

                result = tool_function(**arguments)

            print("Tool result:", result)

            # ------------------------------------------------
            # SEND TOOL RESULT BACK TO THE MODEL
            # ------------------------------------------------
            #
            # This is the important part of the tool loop.
            #
            # LLM requested:
            #
            #     fetch_course("python101")
            #
            # Python executed it.
            #
            # Now we tell the LLM what Python returned.

            messages.append(
                {
                    "role": "tool",

                    "tool_call_id": tool_call.id,

                    "content": json.dumps(result)
                }
            )

    # ========================================================
    # ITERATION CAP REACHED
    # ========================================================

    raise RuntimeError(
        f"TooManySteps: tool loop exceeded "
        f"the maximum of {max_steps} steps."
    )


# ============================================================
# 8. PLAIN PYTHON VERSION OF THE CALCULATION
# ============================================================
# This version does NOT involve an LLM.
#
# This demonstrates concept 2.32:
#
# Do NOT use an LLM when the task is deterministic.


def calculate_total_without_llm(
    price: float,
    quantity: int
):
    """
    Calculate the total directly with Python.
    No LLM is required.
    """

    return price * quantity


# ============================================================
# 9. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("TASK 2.5 — TOOL LOOP")
    print("=" * 60)

    # --------------------------------------------------------
    # NORMAL TOOL LOOP
    # --------------------------------------------------------

    print("\n")
    print("NORMAL TOOL LOOP")
    print("-" * 60)

    try:

        run_tool_loop(
            "Tell me about Python Basics"
        )

    except RuntimeError as error:

        print("\nERROR:")
        print(error)


    # ========================================================
    # 10. ITERATION CAP DEMONSTRATION
    # ========================================================

    print("\n")
    print("=" * 60)
    print("ITERATION CAP DEMONSTRATION")
    print("=" * 60)

    try:

        # Deliberately allow only ONE model iteration.
        #
        # The model will request fetch_course.
        # The tool will execute.
        # But the loop is not allowed to continue
        # to the second model call.

        run_tool_loop(
            "Tell me about Python Basics",
            max_steps=1
        )

    except RuntimeError as error:

        print("\nCAP TRIGGERED:")
        print(error)


    # ========================================================
    # 11. PLAIN PYTHON — NO LLM
    # ========================================================

    print("\n")
    print("=" * 60)
    print("PLAIN PYTHON — NO LLM")
    print("=" * 60)

    price = 1000
    quantity = 3

    total = calculate_total_without_llm(
        price,
        quantity
    )

    print(f"Price: {price}")
    print(f"Quantity: {quantity}")
    print(f"Total: {total}")


    # ========================================================
    # 12. CONCLUSION
    # ========================================================

    print("\n")
    print("=" * 60)
    print("CONCLUSION")
    print("=" * 60)

    print(
        """
The LLM was not needed for calculate_total_without_llm()
because multiplication is deterministic.

Normal Python is faster, cheaper, predictable, and easy
to test for deterministic calculations.

The LLM is useful when the system needs to understand
natural language and decide which tool should be used.

However, deterministic operations should normally remain
plain Python code instead of using an LLM.
"""
    )