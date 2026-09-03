import asyncio

from main import ask_question


async def main():

    context = "Python was created by Guido van Rossum."

    question = "Who created Python?"

    answer = await ask_question(
        context=context,
        question=question,
    )

    print("Answer:", answer)


if __name__ == "__main__":
    asyncio.run(main())