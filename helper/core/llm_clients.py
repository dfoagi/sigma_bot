from google import genai
from openai import OpenAI
import anthropic

from config import PROXYAPI_KEY, OPENAI_BASE_URL


openai_client = OpenAI(api_key=PROXYAPI_KEY, base_url=OPENAI_BASE_URL)

anthropic_client = anthropic.Anthropic(
    api_key=PROXYAPI_KEY, 
    base_url="https://api.proxyapi.ru/anthropic"
    )

genai_client = genai.Client(
    api_key=PROXYAPI_KEY, 
    http_options={"base_url": "https://api.proxyapi.ru/google"}
    )
