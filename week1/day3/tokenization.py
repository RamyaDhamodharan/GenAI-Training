import os
import time
import httpx
import tiktoken
import logging
from dotenv import load_dotenv


# Load .env
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}


# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Prompt
prompt = "Explain what Python is in one simple sentence."


# --------------------------------------------------
# 1. Count tokens BEFORE API call
# --------------------------------------------------

encoding = tiktoken.get_encoding("cl100k_base")

local_prompt_tokens = len(encoding.encode(prompt))

print("Local Prompt tokens:", local_prompt_tokens)


# --------------------------------------------------
# 2. Payload
# --------------------------------------------------

payload = {
    "model": "openai/gpt-4o-mini",
    "messages": [
        {
            "role": "user",
            "content": prompt,
        }
    ],
}


# --------------------------------------------------
# 3. Start timer
# --------------------------------------------------

start = time.perf_counter()


# --------------------------------------------------
# 4. API call
# --------------------------------------------------

response = httpx.post(
    url,
    headers=headers,
    json=payload,
    timeout=30.0,
)


# --------------------------------------------------
# 5. Stop timer
# --------------------------------------------------

end = time.perf_counter()


# --------------------------------------------------
# 6. Check response
# --------------------------------------------------

response.raise_for_status()

data = response.json()


# --------------------------------------------------
# 7. Calculate latency
# --------------------------------------------------

latency_ms = (end - start) * 1000


# --------------------------------------------------
# 8. Get usage information from OpenRouter
# --------------------------------------------------

usage = data["usage"]

prompt_tokens = usage["prompt_tokens"]
completion_tokens = usage["completion_tokens"]
total_tokens = usage["total_tokens"]

# IMPORTANT:
# Use the actual cost returned by OpenRouter
cost_usd = usage["cost"]


# --------------------------------------------------
# 9. Convert USD to INR
# --------------------------------------------------

usd_to_inr = 82.0

cost_inr = cost_usd * usd_to_inr


# --------------------------------------------------
# 10. Print answer
# --------------------------------------------------

print("\nANSWER:")
print(data["choices"][0]["message"]["content"])


# --------------------------------------------------
# 11. Print report
# --------------------------------------------------

print("\nREPORT:")

print("Prompt tokens:", prompt_tokens)
print("Completion tokens:", completion_tokens)
print("Total tokens:", total_tokens)
print("Latency (ms):", latency_ms)
print("Cost (USD):", cost_usd)
print("Cost (INR):", cost_inr)


# --------------------------------------------------
# 12. Structured logging
# --------------------------------------------------

logger.info(
    "model_call "
    "model=%s "
    "prompt_tokens=%d "
    "completion_tokens=%d "
    "latency_ms=%.2f "
    "cost_usd=%.10f "
    "cost_inr=%.10f",
    data["model"],
    prompt_tokens,
    completion_tokens,
    latency_ms,
    cost_usd,
    cost_inr,
)