import asyncio
import os
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()

async def list_models():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY saknas i miljövariabler eller .env!")

    client = AsyncAnthropic(api_key=api_key)
    models = await client.models.list()

    # models kan vara lista av tuples (id, namn, typ) eller dict
    for m in models:
        # om tuple
        if isinstance(m, tuple):
            print("Model ID:", m[0])
        # om dict
        elif isinstance(m, dict):
            print("Model ID:", m.get("id"))
        else:
            print("Model:", m)

asyncio.run(list_models())