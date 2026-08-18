import time
import httpx


URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"


def read_prompts():
    prompts = []

    with open("prompts.txt", "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            prompt_id, prompt = line.split("|", 1)

            prompts.append({
                "id": prompt_id,
                "prompt": prompt
            })

    return prompts


def call_model(prompt):

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }

    start = time.perf_counter()

    try:
        response = httpx.post(
            URL,
            json=payload,
            timeout=120
        )

        latency = time.perf_counter() - start

        response.raise_for_status()

        data = response.json()

        output = data["message"]["content"]

        return {
            "success": True,
            "output": output,
            "latency": latency
        }

    except Exception as error:

        latency = time.perf_counter() - start

        return {
            "success": False,
            "output": "",
            "latency": latency,
            "error": str(error)
        }


def main():

    prompts = read_prompts()

    print("=" * 70)
    print("OLLAMA LOCAL BAKE-OFF")
    print("=" * 70)

    print(f"Model: {MODEL}")
    print(f"Number of prompts: {len(prompts)}")

    with open("ollama_results.txt", "w", encoding="utf-8") as file:

        for index, prompt_data in enumerate(prompts, start=1):

            prompt_id = prompt_data["id"]
            prompt = prompt_data["prompt"]

            print(
                f"\n[{index}/{len(prompts)}] Running {prompt_id}..."
            )

            result = call_model(prompt)

            print(
                f"Latency: {result['latency']:.3f} seconds"
            )

            if result["success"]:

                print("✓ SUCCESS")

                file.write("\n" + "=" * 70 + "\n")
                file.write(f"MODEL: {MODEL}\n")
                file.write(f"PROMPT: {prompt_id}\n")
                file.write("=" * 70 + "\n")

                file.write("\nPrompt:\n")
                file.write(prompt + "\n")

                file.write("\nLatency:\n")
                file.write(
                    f"{result['latency']:.3f} seconds\n"
                )

                file.write("\nResponse:\n")
                file.write(result["output"] + "\n")

                file.write("\nUsable: PENDING\n")

            else:

                print("✗ FAILED")
                print(result["error"])


if __name__ == "__main__":
    main()