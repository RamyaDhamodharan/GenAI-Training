# LangChain Comparison

## Objective

Task 3.3 requires comparing the original direct implementation with the LangChain implementation.

Both implementations perform the same task:

```text
Context + Question
        ↓
Prompt
        ↓
Qwen model through OpenRouter
        ↓
Answer
```

---

## 1. Prompt Construction

### Direct Implementation

In `direct/main.py`, the prompt is manually created using a Python f-string.

```python
prompt = f"""
Answer only from the given context.

Context:
{context}

Question:
{question}
"""
```

The application is responsible for constructing the complete prompt string.

### LangChain Implementation

LangChain uses `ChatPromptTemplate`.

```python
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Answer only from the given context."
    ),
    (
        "human",
        "Context:\n{context}\n\nQuestion:\n{question}"
    )
])
```

The variables are defined as named placeholders.

### What did LangChain hide?

LangChain hides some of the manual prompt formatting and message construction.

### Worth handing over?

**YES**

For larger applications, reusable prompt templates are easier to maintain than manually constructing strings everywhere.

---

## 2. Model API Call

### Direct Implementation

The direct implementation creates an `AsyncOpenAI` client.

```python
client = AsyncOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)
```

Then the application manually calls:

```python
response = await client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
)
```

The application directly controls the API request.

### LangChain Implementation

LangChain uses `ChatOpenAI`.

```python
model = ChatOpenAI(
    model="qwen/qwen-2.5-7b-instruct",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)
```

The application does not directly construct the chat completion request.

### What did LangChain hide?

LangChain hides the lower-level model invocation details and provides a common chat-model interface.

### Worth handing over?

**YES, with caution**

It is useful when the application works with multiple models or providers.

However, developers should still understand the underlying API because debugging provider-specific problems may require that knowledge.

---

## 3. Response Extraction

### Direct Implementation

The direct implementation manually extracts the model's response.

```python
answer = response.choices[0].message.content
```

The application needs to know the structure of the API response.

### LangChain Implementation

LangChain uses:

```python
parser = StrOutputParser()
```

The parser converts the model output into a string.

### What did LangChain hide?

LangChain hides the manual response extraction and conversion.

### Worth handing over?

**YES**

For simple string responses, this removes repetitive response handling code.

For structured responses, additional validation may still be required.

---

## 4. Connecting the Components

### Direct Implementation

The direct implementation explicitly performs each operation:

```text
Create prompt
      ↓
Call model
      ↓
Extract response
```

The developer manually controls the flow.

### LangChain Implementation

LangChain uses LCEL:

```python
chain = prompt | model | parser
```

This creates a pipeline:

```text
Prompt
  ↓
Model
  ↓
Parser
```

The output of one component becomes the input of the next component.

### What did LangChain hide?

LangChain hides much of the glue code required to pass data between components.

### Worth handing over?

**YES**

This becomes especially useful when chains contain many components.

For a single model call, however, the direct implementation is simpler.

---

## 5. Callback Hooks

LangChain provides callback hooks around chain and model execution.

Conceptually:

```text
Chain starts
     ↓
Model starts
     ↓
Model completes
     ↓
Parser completes
     ↓
Chain completes
```

These hooks can later be connected to observability and tracing systems such as Langfuse.

### What will be attached in Week 6?

The callback hook can be used to capture information such as:

* Request/trace information
* Model execution
* Latency
* Token usage
* Errors
* Chain execution

This allows the application to observe the LLM workflow without manually adding logging around every component.

### Worth handing over?

**YES**

For production LLM applications, tracing and observability become important.

---

## 6. What LangChain Hides

| Responsibility       | Direct Implementation  | LangChain            | Worth handing over? |
| -------------------- | ---------------------- | -------------------- | ------------------- |
| Prompt construction  | Manual f-string        | `ChatPromptTemplate` | YES                 |
| Model invocation     | `AsyncOpenAI` API call | `ChatOpenAI`         | YES, with caution   |
| Response extraction  | `response.choices...`  | `StrOutputParser`    | YES                 |
| Component connection | Manual Python flow     | LCEL `\|`            | YES                 |
| Execution hooks      | Manual instrumentation | Callback system      | YES                 |

---

## 7. What Should NOT Be Completely Hidden?

LangChain makes development easier, but developers should still understand what happens underneath.

Important concepts to understand:

* HTTP/API requests
* Authentication
* Model provider APIs
* Prompt construction
* Response formats
* Token usage
* Timeouts
* Retries
* Errors
* Streaming
* Logging
* Observability

Using LangChain without understanding these concepts can make debugging difficult.

---

## 8. Final Judgment

LangChain is useful when the application contains multiple LLM components, reusable prompts, output parsing, retrieval, tools, callbacks, or complex chains.

For a single simple model call, the direct implementation can be easier to understand and debug.

Therefore, LangChain should be used when it removes meaningful complexity rather than simply because it is a popular framework.

The direct implementation remains valuable because it shows what LangChain is doing underneath.
