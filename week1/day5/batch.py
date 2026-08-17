import os
import time
import asyncio
import httpx
from dotenv import load_dotenv


# ==================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ==================================================

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}


# ==================================================
# 2. READ PROMPTS FROM FILE
# ==================================================

with open("prompts.txt", "r", encoding="utf-8") as file:

    prompts = [
        line.strip()
        for line in file
        if line.strip()
    ]


print("Number of prompts:", len(prompts))


# ==================================================
# 3. API CALL FUNCTION
# ==================================================

async def call_api(client, prompt):

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0,
    }

    response = await client.post(
        url,
        headers=headers,
        json=payload,
        timeout=30.0,
    )

    response.raise_for_status()

    data = response.json()

    answer = data["choices"][0]["message"]["content"]

    usage = data["usage"]

    return {
        "prompt": prompt,
        "answer": answer,
        "prompt_tokens": usage["prompt_tokens"],
        "completion_tokens": usage["completion_tokens"],
        "total_tokens": usage["total_tokens"],
        "cost_usd": usage["cost"],
    }


# ==================================================
# 4. SEQUENTIAL EXECUTION
# ==================================================

async def run_sequential(client, prompts):

    results = []

    start = time.perf_counter()

    for prompt in prompts:

        result = await call_api(client, prompt)

        results.append(result)

    end = time.perf_counter()

    elapsed = end - start

    return results, elapsed


# ==================================================
# 5. CONCURRENT EXECUTION
# ==================================================

async def run_concurrent(client, prompts):

    start = time.perf_counter()

    tasks = [
        call_api(client, prompt)
        for prompt in prompts
    ]

    results = await asyncio.gather(*tasks)

    end = time.perf_counter()

    elapsed = end - start

    return results, elapsed


# ==================================================
# 6. COST REPORT
# ==================================================

def calculate_cost(results):

    total_cost = sum(
        result["cost_usd"]
        for result in results
    )

    average_cost = (
        total_cost / len(results)
        if results
        else 0
    )

    total_tokens = sum(
        result["total_tokens"]
        for result in results
    )

    return total_tokens, total_cost, average_cost


# ==================================================
# 7. PRINT RESULTS
# ==================================================

def print_results(title, results):

    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)

    for i, result in enumerate(results, start=1):

        print(f"\n--- Prompt {i} ---")
        print("Question:", result["prompt"])

        print("\nAnswer:")
        print(result["answer"])

        print("\nUsage:")
        print(
            "Prompt tokens:",
            result["prompt_tokens"]
        )

        print(
            "Completion tokens:",
            result["completion_tokens"]
        )

        print(
            "Total tokens:",
            result["total_tokens"]
        )

        print(
            "Cost (USD):",
            result["cost_usd"]
        )


# ==================================================
# 8. MAIN
# ==================================================

async def main():

    async with httpx.AsyncClient() as client:

        # ------------------------------------------
        # Sequential
        # ------------------------------------------

        print("\nRunning sequential requests...")

        sequential_results, sequential_time = (
            await run_sequential(
                client,
                prompts
            )
        )

        print_results(
            "SEQUENTIAL RESULTS",
            sequential_results
        )

        sequential_tokens, sequential_cost, sequential_average = (
            calculate_cost(sequential_results)
        )


        # ------------------------------------------
        # Concurrent
        # ------------------------------------------

        print("\nRunning concurrent requests...")

        concurrent_results, concurrent_time = (
            await run_concurrent(
                client,
                prompts
            )
        )

        print_results(
            "CONCURRENT RESULTS",
            concurrent_results
        )

        concurrent_tokens, concurrent_cost, concurrent_average = (
            calculate_cost(concurrent_results)
        )


        # ==================================================
        # 9. FINAL COMPARISON
        # ==================================================

        print("\n" + "=" * 50)
        print("FINAL BATCH REPORT")
        print("=" * 50)

        print(
            f"\nNumber of prompts: {len(prompts)}"
        )

        print("\n--- Sequential ---")

        print(
            f"Elapsed time: "
            f"{sequential_time:.2f} seconds"
        )

        print(
            f"Total tokens: "
            f"{sequential_tokens}"
        )

        print(
            f"Total cost: "
            f"${sequential_cost:.8f}"
        )

        print(
            f"Average cost per prompt: "
            f"${sequential_average:.8f}"
        )


        print("\n--- Concurrent ---")

        print(
            f"Elapsed time: "
            f"{concurrent_time:.2f} seconds"
        )

        print(
            f"Total tokens: "
            f"{concurrent_tokens}"
        )

        print(
            f"Total cost: "
            f"${concurrent_cost:.8f}"
        )

        print(
            f"Average cost per prompt: "
            f"${concurrent_average:.8f}"
        )


        # ------------------------------------------
        # Speed comparison
        # ------------------------------------------

        print("\n--- Performance Comparison ---")

        if concurrent_time < sequential_time:

            improvement = (
                (sequential_time - concurrent_time)
                / sequential_time
            ) * 100

            print(
                f"Concurrent execution was "
                f"{improvement:.2f}% faster."
            )

        else:

            print(
                "Concurrent execution was not faster "
                "in this particular run."
            )


# ==================================================
# 10. START PROGRAM
# ==================================================

asyncio.run(main())