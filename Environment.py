import asyncio
import os
from contextlib import AsyncExitStack
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import AsyncAnthropic

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ZUBE_PATH = os.path.join(BASE_DIR, "zube.js")


async def run_mcp_claude_client():

    # CONFIG
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
    anthropic_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    async with AsyncExitStack() as exit_stack:

        server_params = StdioServerParameters(
            command="node",
            args=["zube.js"],
            cwd=BASE_DIR,
            env=os.environ.copy()
        )

        stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
        read, write = stdio_transport
        mcp_session = await exit_stack.enter_async_context(ClientSession(read, write))

        await mcp_session.initialize()

        mcp_tools = await mcp_session.list_tools()
        claude_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool in mcp_tools.tools
        ]

        query = "Show me the current status of my Zube tasks."
        messages = [{"role": "user", "content": query}]

        print(f"User: {query}\n")

        # Agentic loop — keeps running until Claude stops calling tools
        while True:
            response = await anthropic_client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=4096,
                messages=messages,
                tools=claude_tools
            )

            # Append Claude's response to the conversation
            messages.append({"role": "assistant", "content": response.content})

            # If Claude is done (no more tool calls), print final answer and exit
            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text"):
                        print("\nClaude's Final Response:")
                        print(block.text)
                break

            # Process all tool calls in this response turn
            if response.stop_reason == "tool_use":
                tool_results = []

                for block in response.content:
                    if block.type == "tool_use":
                        print(f"  → Calling tool: {block.name} with args: {block.input}")
                        result = await mcp_session.call_tool(block.name, block.input)
                        result_text = str(result.content)
                        print(f"  ← Tool result: {result_text[:200]}{'...' if len(result_text) > 200 else ''}\n")

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_text
                        })

                # Feed all tool results back as a single user message
                messages.append({"role": "user", "content": tool_results})

            else:
                # Unexpected stop reason — bail out safely
                print(f"Unexpected stop_reason: {response.stop_reason}")
                break


if __name__ == "__main__":
    asyncio.run(run_mcp_claude_client())