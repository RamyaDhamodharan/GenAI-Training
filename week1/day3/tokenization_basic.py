import tiktoken
import time

encoding = tiktoken.get_encoding("cl100k_base")

text = "unhappiness"

tokens = encoding.encode(text)

print("Text:", text)
print("Token IDs:", tokens)
print("Number of tokens:", len(tokens))

pieces = [encoding.decode([token]) for token in tokens]

print("Token pieces:", pieces)
print(tiktoken.list_encoding_names())

prompt = "Explain what Python is in one simple sentence."
tokens = encoding.encode(prompt)

print("Prompt tokens:", len(tokens))
start = time.perf_counter()

end = time.perf_counter()
latency_ms = (end - start) * 1000
print("Latency (ms):", latency_ms)
