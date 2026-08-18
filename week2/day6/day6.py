import os
import time
import httpx
from dotenv import load_dotenv


# ==========================================
# 1. LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env file")


# ==========================================
# 2. OPENROUTER CONFIGURATION
# ==========================================

URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


# ==========================================
# 3. READ PROMPTS FROM prompts.txt
# ==========================================

def read_prompts():

    prompts = []

    with open("prompts.txt", "r", encoding="utf-8") as file:

        for line in file:

            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            prompt_id, prompt = line.split("|", 1)

            prompts.append({
                "id": prompt_id,
                "prompt": prompt
            })

    return prompts


# ==========================================
# 4. READ MODELS FROM models.txt
# ==========================================

def read_models():

    models = []

    with open("models.txt", "r", encoding="utf-8") as file:

        for line in file:

            if line.strip():
                models.append(line.strip())

    return models


# ==========================================
# 5. CALL OPENROUTER
# ==========================================

def call_model(model, prompt):

    payload = {

        "model": model,

        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
    }

    start = time.perf_counter()

    try:

        response = httpx.post(
            URL,
            headers=HEADERS,
            json=payload,
            timeout=60,
        )

        latency = time.perf_counter() - start

        response.raise_for_status()

        data = response.json()

        # Generated answer
        output = data["choices"][0]["message"]["content"]

        # Token and cost information
        usage = data.get("usage", {})

        return {
            "success": True,
            "output": output,
            "latency": latency,
            "usage": usage,
            "error": None
        }

    except Exception as error:

        latency = time.perf_counter() - start

        return {
            "success": False,
            "output": "",
            "latency": latency,
            "usage": {},
            "error": str(error)
        }


# ==========================================
# 6. SAVE RESULT TO results.txt
# ==========================================

def save_result(
    file,
    model,
    prompt_id,
    prompt,
    result
):

    file.write("\n")
    file.write("=" * 70 + "\n")
    file.write(f"MODEL: {model}\n")
    file.write(f"PROMPT: {prompt_id}\n")
    file.write("=" * 70 + "\n")

    file.write("\nPrompt:\n")
    file.write(prompt + "\n")

    file.write("\nLatency:\n")
    file.write(f"{result['latency']:.3f} seconds\n")

    if result["success"]:

        usage = result["usage"]

        file.write("\nUsage:\n")

        file.write(
            f"Prompt tokens: "
            f"{usage.get('prompt_tokens', 'N/A')}\n"
        )

        file.write(
            f"Completion tokens: "
            f"{usage.get('completion_tokens', 'N/A')}\n"
        )

        file.write(
            f"Total tokens: "
            f"{usage.get('total_tokens', 'N/A')}\n"
        )

        file.write(
            f"Cost: "
            f"${usage.get('cost', 'N/A')}\n"
        )

        file.write("\nResponse:\n")
        file.write(result["output"] + "\n")

        file.write("\nUsable: PENDING\n")
        file.write("Failure: NONE\n")

    else:

        file.write("\nAPI CALL FAILED\n")
        file.write(f"Error: {result['error']}\n")


# ==========================================
# 7. MAIN PROGRAM
# ==========================================

def main():

    # Read prompts and models
    prompts = read_prompts()
    models = read_models()


    # ==========================================
    # CREATE SUMMARY STORAGE
    # ==========================================

    summary = {}

    for model in models:

        summary[model] = {

            "total_latency": 0,

            "total_cost": 0,

            "successful": 0,

            "failed": 0
        }


    # ==========================================
    # START BAKE-OFF
    # ==========================================

    print("=" * 70)
    print("MODEL BAKE-OFF")
    print("=" * 70)

    print(f"\nNumber of prompts: {len(prompts)}")
    print(f"Number of models: {len(models)}")
    print(f"Total API calls: {len(prompts) * len(models)}")

    print("\nStarting...\n")


    # ==========================================
    # OPEN RESULTS FILE
    # ==========================================

    with open(
        "results.txt",
        "w",
        encoding="utf-8"
    ) as results_file:

        results_file.write("=" * 70 + "\n")
        results_file.write("MODEL BAKE-OFF RESULTS\n")
        results_file.write("=" * 70 + "\n")

        results_file.write(
            f"\nTotal prompts: {len(prompts)}\n"
        )

        results_file.write(
            f"Total models: {len(models)}\n"
        )

        results_file.write(
            f"Total API calls: "
            f"{len(prompts) * len(models)}\n"
        )


        # ==========================================
        # MODEL LOOP
        # ==========================================

        for model_index, model in enumerate(
            models,
            start=1
        ):

            print(
                f"\n[{model_index}/{len(models)}] "
                f"MODEL: {model}"
            )


            # ==========================================
            # PROMPT LOOP
            # ==========================================

            for prompt_index, prompt_data in enumerate(
                prompts,
                start=1
            ):

                prompt_id = prompt_data["id"]

                prompt = prompt_data["prompt"]

                print(
                    f"  [{prompt_index}/{len(prompts)}] "
                    f"Running {prompt_id}..."
                )


                # Call model
                result = call_model(
                    model,
                    prompt
                )


                # Save detailed result
                save_result(
                    results_file,
                    model,
                    prompt_id,
                    prompt,
                    result
                )


                # ==========================================
                # UPDATE SUMMARY
                # ==========================================

                if result["success"]:

                    usage = result["usage"]

                    summary[model]["total_latency"] += (
                        result["latency"]
                    )

                    summary[model]["total_cost"] += (
                        usage.get("cost", 0) or 0
                    )

                    summary[model]["successful"] += 1

                    print(
                        f"      ✓ SUCCESS | "
                        f"{result['latency']:.3f}s | "
                        f"${usage.get('cost', 'N/A')}"
                    )

                else:

                    summary[model]["failed"] += 1

                    print(
                        f"      ✗ FAILED | "
                        f"{result['error']}"
                    )


    # ==========================================
    # FINAL COMPARISON
    # ==========================================

    print("\n" + "=" * 70)
    print("BAKE-OFF COMPLETED")
    print("=" * 70)


    for model, data in summary.items():

        total_calls = (
            data["successful"]
            + data["failed"]
        )


        if total_calls > 0:

            average_latency = (
                data["total_latency"]
                / total_calls
            )

        else:

            average_latency = 0


        print(f"\nModel: {model}")

        print(
            f"Average latency: "
            f"{average_latency:.3f} seconds"
        )

        print(
            f"Total cost: "
            f"${data['total_cost']:.8f}"
        )

        print(
            f"Successful: "
            f"{data['successful']}/{total_calls}"
        )

        print(
            f"Failed: "
            f"{data['failed']}/{total_calls}"
        )


    print("\nResults saved to: results.txt")


# ==========================================
# 8. PYTHON ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()