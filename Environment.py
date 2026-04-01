import asyncio
import os
import json
import sqlite3
from contextlib import AsyncExitStack
from dotenv import load_dotenv
import time
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import AsyncAnthropic
from anthropic.types import MessageParam, ToolParam

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db.js")


def get_prompts_from_db() -> list[tuple[int, str]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, prompt FROM prompts")
    rows = cursor.fetchall()
    conn.close()
    return rows


def save_to_db(
    prompt: str,
    response: str,
    tool_invocation: bool,
    tools_used: list[str],
    tool_inputs: list[dict[str, Any]],
    duration_ms: int,
) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM prompts WHERE prompt = ?", (prompt,))
    row = cursor.fetchone()
    prompt_id: int | None = row[0] if row else None
    rouge_l_f1 = None
    cursor.execute(
        """INSERT INTO mcp_tools 
           (prompt_id, response, rouge_l_f1, tool_invocation, 
            tools_used, tool_inputs, duration_ms)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            prompt_id,
            response,
            rouge_l_f1,
            1 if tool_invocation else 0,
            json.dumps(tools_used),
            json.dumps(tool_inputs),
            duration_ms,
        ),
    )
    conn.commit()
    conn.close()


async def run_query(
    anthropic_client: AsyncAnthropic,
    mcp_session: ClientSession,
    claude_tools: list[ToolParam],
    model: str,
    query: str,
) -> tuple[str, list[str], list[dict[str, Any]], int]:
    messages: list[MessageParam] = [{"role": "user", "content": query}]
    print(f"\nUser: {query}\n")

    tools_used: list[str] = []
    tool_inputs: list[dict[str, Any]] = []
    final_response: str = ""
    start_time = time.time()

    while True:
        response = await anthropic_client.messages.create(
            model=model,
            max_tokens=4096,
            messages=messages,
            tools=claude_tools,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    final_response = block.text
                    print("\nClaude's Final Response:")
                    print(block.text)
            break

        if response.stop_reason == "tool_use":
            tool_results: list[dict[str, Any]] = []

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
                        "content": result_text,
                    })

            messages.append({"role": "user", "content": tool_results})

        else:
            print(f"Unexpected stop_reason: {response.stop_reason}")
            break

    duration_ms = int((time.time() - start_time) * 1000)
    return final_response, tools_used, tool_inputs, duration_ms


async def run_mcp_claude_client() -> None:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
    anthropic_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    prompts = get_prompts_from_db()
    if not prompts:
        print("No prompts found in prompts table.")
        return

    print(f"Found {len(prompts)} prompt(s) to run.\n")

    async with AsyncExitStack() as exit_stack:
        server_params = StdioServerParameters(
            command="node",
            args=["zube.js"],
            cwd=BASE_DIR,
            env=os.environ.copy(),
        )

        stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
        read, write = stdio_transport
        mcp_session = await exit_stack.enter_async_context(ClientSession(read, write))

        await mcp_session.initialize()

        mcp_tools = await mcp_session.list_tools()
        claude_tools: list[ToolParam] = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in mcp_tools.tools
        ]

        for ref_id, query in prompts:
            print(f"--- Running prompt id={ref_id} ---")
            final_response, tools_used, tool_inputs, duration_ms = await run_query(
                anthropic_client, mcp_session, claude_tools, ANTHROPIC_MODEL, query
            )

            save_to_db(
                prompt=query,
                response=final_response,
                tool_invocation=len(tools_used) > 0,
                tools_used=tools_used,
                tool_inputs=tool_inputs,
                duration_ms=duration_ms,
            )
            print(f"✓ Saved — {len(tools_used)} tool(s) used in {duration_ms}ms")


if __name__ == "__main__":
    asyncio.run(run_mcp_claude_client())