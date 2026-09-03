import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


# Load the common .env from GenAI-Training/
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)


# Create the chat model
model = ChatOpenAI(
    model="qwen/qwen-2.5-7b-instruct",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


# Create prompt template
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


# Create output parser
parser = StrOutputParser()


# Connect everything using LCEL
chain = prompt | model | parser


async def ask_question(context: str, question: str):

    result = await chain.ainvoke({
        "context": context,
        "question": question,
    })

    return result