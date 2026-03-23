import asyncio
import time
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
import os
from anthropic import Anthropic
load_dotenv()

ATHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
anthropic = Anthropic(api_key=ATHROPIC_API_KEY)
ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"

