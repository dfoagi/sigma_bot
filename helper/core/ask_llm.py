from google import genai
from openai import OpenAI
import anthropic
import asyncio

from helper.core.qdrant_client import get_relevant_chunks
from helper.core.llm_clients import openai_client, anthropic_client, genai_client
from helper.core.model_state import get_current_topk


def ask_chatgpt(client: OpenAI, context: str, user_question: str, model: str) -> dict:

    my_messages = [
        {"role": "system", "content": "Ты помощник по продукту. Отвечай ясно и по делу, как специалист техподдержки. На языке, котором задали вопрос"},
        {"role": "user", "content": f"""
        Вот часть руководства, в которой нужно смотреть:

        {context}

        Вопрос пользователя: {user_question}

        Ответь максимально точно, используя только предоставленный текст. Если ответ найден, укажи в какой главе
        руководства пользователя можно посмотреть подробнее.
        Если ответа точно нет в тексте, скажи честно, что ответ ты не нашел и попроси переформулировать вопрос либо
        обратиться к службе технической поддержки."""}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=my_messages
    )

    answer = response.choices[0].message.content
    prompt_tokens = response.usage.prompt_tokens
    response_tokens = response.usage.completion_tokens
    used_model = response.model

    return answer, prompt_tokens, response_tokens, used_model


def ask_anthropic(client: anthropic.Anthropic, context: str, user_question: str, model: str):

    response = client.messages.create(
        model=model,
        max_tokens=1000,
        system="Ты помощник по продукту. Отвечай ясно и по делу, как специалист техподдержки. На языке, котором задали вопрос",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
                            Вот часть руководства, в которой нужно смотреть:

                            {context}

                            Вопрос пользователя: {user_question}

                            Ответь максимально точно, используя только предоставленный текст.
                            Если ответ найден, укажи в какой главе руководства пользователя можно посмотреть подробнее.
                            Если ответа точно нет в тексте, скажи честно, что ответ ты не нашел и попроси переформулировать вопрос либо
                            обратиться к службе технической поддержки.
                            В ответе используй только стандартные символы ASCII или символы, совместимые с Windows-1251. Не используй 
                            эмодзи, стрелки, математические символы и другие спецсимволы."""
                    }
                ]
            }
        ]
    )

    answer = response.content[0].text
    prompt_tokens = response.usage.input_tokens
    response_tokens = response.usage.output_tokens
    used_model = response.model

    return answer, prompt_tokens, response_tokens, used_model


def ask_gemini(client: genai.Client, context: str, user_question: str, model: str):

    response = client.models.generate_content(
        model=model,
        config=genai.types.GenerateContentConfig(
            system_instruction="Ты помощник по продукту. Отвечай ясно и по делу, как специалист техподдержки. На языке, котором задали вопрос"),
        contents=f"""
            Вот часть руководства и отдельных ответов, в которых нужно смотреть:

            {context}

            Вопрос пользователя: {user_question}

            Ответь максимально точно, используя только предоставленный текст.

            Если ответ найден и в начале фрагмента указан номер главы и её название, укажи в какой главе руководства пользователя
            можно посмотреть подробнее. Если название главы не указано, то просто дай ответ на вопрос. Если есть ссылка на видео,
            в котором есть ответ на вопрос пользователя, поделись с ним этой ссылкой

            Если ответа точно нет в тексте, скажи честно, что ответ ты не нашел и попроси переформулировать вопрос либо
            обратиться к службе технической поддержки. Так же в новом абзаце поблагодари пользователя за вопрос, скажи ему, что база
            данных обновляется и в скором времени ответ на его вопрос появится.

            В ответе используй только стандартные символы ASCII или символы, совместимые с Windows-1251. Не используй 
            эмодзи, стрелки, математические символы и другие спецсимволы.
            Для выделения текста можешь использовать следующие теги: <b>bold</b>, <i>italic</i>, <u>underline</u>. Другие теги не 
            поддерживаются!
            """
    )

    answer = response.candidates[0].content.parts[0].text
    prompt_tokens = response.usage_metadata.prompt_token_count
    response_tokens = response.usage_metadata.candidates_token_count
    used_model = response.model_version

    return answer, prompt_tokens, response_tokens, used_model


async def ask_llm(context: str, user_question: str, model: str):
    model = model.lower()

    if model.startswith("gpt") or model == "o4-mini-2025-04-16":
        return await asyncio.to_thread(ask_chatgpt, openai_client, context, user_question, model)

    elif model.startswith("claude"):
        return await asyncio.to_thread(ask_anthropic, anthropic_client, context, user_question, model)

    elif model.startswith("gemini"):
        return await asyncio.to_thread(ask_gemini, genai_client, context, user_question, model)

    raise ValueError(f"Неизвестная модель: {model}")


async def get_answer(user_question: str, qdrant_client, collection_name: str, model: str, top_k=3):
    embedding_response = await asyncio.to_thread(
        lambda: openai_client.embeddings.create(  # только для embedding
            model="text-embedding-3-large",
            input=user_question
        )
    )
    question_vector = embedding_response.data[0].embedding

    top_k = get_current_topk()

    relevant_chunks = get_relevant_chunks(
        client=qdrant_client,
        collection_name=collection_name,
        question_vector=question_vector,
        top_k=top_k
    )

    chapter_ids = " ".join(str(p.id) for p in relevant_chunks.points)
    chapter_scores = " ".join(str(p.score) for p in relevant_chunks.points)
    context_text = "\n\n".join(p.payload['text'] for p in relevant_chunks.points)

    answer, prompt_tokens, response_tokens, used_model = await ask_llm(
        context=context_text,
        user_question=user_question,
        model=model
    )

    return answer, chapter_ids, chapter_scores, prompt_tokens, response_tokens, used_model
