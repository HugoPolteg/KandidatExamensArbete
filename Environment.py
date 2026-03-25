import asyncio
import os
import json
import sqlite3
from contextlib import AsyncExitStack
from dotenv import load_dotenv
import time

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import AsyncAnthropic

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ZUBE_PATH = os.path.join(BASE_DIR, "zube.js")
DB_PATH = os.path.join(BASE_DIR, "db.js")

def save_to_db(prompt, response, tool_invocation, tools_used, tool_inputs, duration_ms):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO mcp_tools 
           (prompt, response, correct_response, tool_invocation, correct_tool_invocation, 
            tools_used, correct_tool_use, tool_inputs, correct_tool_inputs, duration_ms)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            prompt,
            response,
            None,   # correct_response — to be filled from reference db later
            1 if tool_invocation else 0,
            None,   # correct_tool_invocation — to be filled from reference db later
            json.dumps(tools_used),
            None,   # correct_tool_use — to be filled from reference db later
            json.dumps(tool_inputs),
            None,   # correct_tool_inputs — to be filled from reference db later
            duration_ms,
        )
    )
    conn.commit()
    conn.close()

async def run_mcp_claude_client():

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

        tools_used = []       # list of tool names called across all turns
        tool_inputs = []      # list of {tool_name, args} dicts across all turns
        final_response = ""
        start_time = time.time()

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

                        tools_used.append(block.name)
                        tool_inputs.append({"tool": block.name, "args": block.input})

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
        
        duration_ms = int((time.time() - start_time) * 1000)

        save_to_db(
            prompt=query,
            response=final_response,
            tool_invocation=len(tools_used) > 0,
            tools_used=tools_used,
            tool_inputs=tool_inputs,
            duration_ms=duration_ms,
        )
        
        print(f"\n✓ Saved to db — {len(tools_used)} tool(s) used in {duration_ms}ms")

if __name__ == "__main__":
    asyncio.run(run_mcp_claude_client())