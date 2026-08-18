1️⃣ P1 — API explanation

Requirement: under 150 words + beginner + one simple example

| Model    | Usable? | Why                               |
| -------- | ------- | --------------------------------- |
| GPT-OSS  | ❌       | Exceeded 150 words                |
| Llama    | ✅       | Simple, relevant, under 150 words |
| DeepSeek | ✅       | Simple + example + under 150      |
| Nemotron | ❌       | Exceeded 150 words                |


2️⃣ P2 — Extract information

Requirement: Extract name, email, phone, issue.

All four extracted the required information correctly.

| Model    | Usable? |
| -------- | ------- |
| GPT-OSS  | ✅       |
| Llama    | ✅       |
| DeepSeek | ✅       |
| Nemotron | ✅       |


3️⃣ P3 — JSON conversion

Requirement: JSON with exactly:

name, age, city, profession

All four produced the correct information in JSON.

| Model    | Usable? |
| -------- | ------- |
| GPT-OSS  | ✅       |
| Llama    | ✅       |
| DeepSeek | ✅       |
| Nemotron | ✅       |

4️⃣ P4 — Discount + GST

Requirement: Correct calculation + show calculation.

All four got:

₹2,360

and showed the calculation.

| Model    | Usable? |
| -------- | ------- |
| GPT-OSS  | ✅       |
| Llama    | ✅       |
| DeepSeek | ✅       |
| Nemotron | ✅       |


5️⃣ P5 — Python function

Requirement: Function should return second-largest unique number and handle fewer than 2 unique numbers.

All four produced a valid solution.

| Model    | Usable? |
| -------- | ------- |
| GPT-OSS  | ✅       |
| Llama    | ✅       |
| DeepSeek | ✅       |
| Nemotron | ✅       |

📊 Final usability table
| Model        | P1 | P2 | P3 | P4 | P5 |  Usable |
| ------------ | -- | -- | -- | -- | -- | ------: |
| **GPT-OSS**  | ❌  | ✅  | ✅  | ✅  | ✅  | **4/5** |
| **Llama**    | ✅  | ✅  | ✅  | ✅  | ✅  | **5/5** |
| **DeepSeek** | ✅  | ✅  | ✅  | ✅  | ✅  | **5/5** |
| **Nemotron** | ❌  | ✅  | ✅  | ✅  | ✅  | **4/5** |

Important observation

Your measured numbers are interesting:

Llama: 5.253s average, $0.00035688
DeepSeek: 10.777s average, $0.00032214
Nemotron: 6.104s average, $0
GPT-OSS: 24.646s average, $0.00051116

But P5 is a huge outlier for GPT-OSS: 97.870 seconds 

So we shouldn't just look at average latency blindly. That's exactly why this bake-off is useful.






ollama 

1. OpenRouter results
| Model             | Avg latency |      Total cost |  Usable |
| ----------------- | ----------: | --------------: | ------: |
| GPT-OSS-120B      |     24.646s |     $0.00051116 |     4/5 |
| Llama 3.3 70B     |  **5.253s** |     $0.00035688 | **5/5** |
| DeepSeek V4 Flash |     10.777s | **$0.00032214** | **5/5** |
| Nemotron 3.5      |      6.104s |          **$0** |     4/5 |

2. Ollama result

Your local model:

llama3.2:3b

| Prompt | Latency |
| ------ | ------: |
| P1     | 16.516s |
| P2     |  7.270s |
| P3     | 18.798s |
| P4     | 15.935s |
| P5     | 16.091s |


Average:

≈ 14.922 seconds

So local Ollama is:

~14.92s average latency, $0 API cost



Ollama usability judgement
| Prompt | Usable? | Reason                                                                                                                          |
| ------ | ------- | ------------------------------------------------------------------------------------------------------------------------------- |
| P1     | ✅       | Correct API explanation, simple example, under 150 words                                                                        |
| P2     | ✅       | All 4 requested fields extracted correctly                                                                                      |
| P3     | ❌       | Prompt asked for the specified JSON fields, but model gave **3 different JSON alternatives** instead of one clean JSON response |
| P4     | ✅       | Correct calculation and final price ₹2,360                                                                                      |
| P5     | ✅       | Correct function and handles fewer than 2 unique numbers                                                                        |

Ollama = 4/5 usable


FINAL COMPARISON
| Model                 | Avg Latency |      Total Cost |  Usable |
| --------------------- | ----------: | --------------: | ------: |
| GPT-OSS 120B          |    24.646 s |     $0.00051116 |     4/5 |
| **Llama 3.3 70B**     | **5.253 s** |     $0.00035688 | **5/5** |
| **DeepSeek V4 Flash** |    10.777 s | **$0.00032214** | **5/5** |
| Nemotron 3.5          |     6.104 s |          **$0** |     4/5 |

Ollama

| Model        |  Avg Latency | API Cost | Usable |
| ------------ | -----------: | -------: | -----: |
| Llama 3.2 3B | **14.922 s** |   **$0** |    4/5 |



Which prompts did each model fail?
| Model               | Failed prompts                                                             |
| ------------------- | -------------------------------------------------------------------------- |
| GPT-OSS 120B        | **P1** — exceeded 150 words                                                |
| Llama 3.3 70B       | **None**                                                                   |
| DeepSeek V4 Flash   | **None**                                                                   |
| Nemotron 3.5        | **P1** — exceeded 150 words                                                |
| Ollama Llama 3.2 3B | **P3** — produced multiple JSON alternatives instead of one requested JSON |




Based on the measured results, I would recommend Llama 3.3 70B for this assistant. It achieved 5/5 usable outputs and had the lowest average latency among the paid models at 5.253 seconds per call, while costing $0.00035688 for the five prompts. DeepSeek V4 Flash also achieved 5/5 usable outputs and had a slightly lower total cost of $0.00032214, but its average latency was higher at 10.777 seconds. Nemotron 3.5 was free and relatively fast at 6.104 seconds, but one prompt failed the usability requirement. The local Ollama Llama 3.2 3B had zero API cost but averaged 14.922 seconds and produced one unusable output. Therefore, based on the measured balance of reliability and latency, Llama 3.3 70B is the best choice for this workload.




5 prompts
   ↓
4 OpenRouter models
   ↓
20 API calls
   ↓
Cost + latency
   ↓
Usability evaluation
   ↓
Ollama installed
   ↓
Llama 3.2 3B locally
   ↓
Same 5 prompts
   ↓
Local latency + usability
   ↓
Comparison
   ↓
Recommendation