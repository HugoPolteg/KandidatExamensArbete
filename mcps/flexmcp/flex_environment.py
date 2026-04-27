import asyncio
import os
import json
import time
import sqlite3
import uuid
from contextlib import AsyncExitStack
from datetime import datetime
from dotenv import load_dotenv
from typing import Any
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import AsyncAnthropic
from anthropic.types import MessageParam, ToolParam
import re

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_JSON_PATH = os.path.join(BASE_DIR, "prompts.json")
DB_PATH = os.path.join(BASE_DIR, "results.db")
TEST_PROMPT_ID = "A-001"


def init_db() -> None:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            interaction_id          TEXT PRIMARY KEY,
            prompt_id               TEXT,
            prompt                  TEXT,
            category                TEXT,
            difficulty              INTEGER,
            expected_outcome        TEXT,
            expected_tool           TEXT,
            expected_query_params   TEXT,
            expected_request_body   TEXT,
            observed_tool           TEXT,
            observed_query_params   TEXT,
            observed_request_body   TEXT,
            correct_tool            INTEGER,
            correct_query_params    INTEGER,
            correct_request_body    INTEGER,
            duration_ms             INTEGER,
            timestamp               TEXT
        )
    """)
    con.commit()
    con.close()


def evaluate_tool(
    correct_solution: list[dict],
    tools_used: list[str],
    tool_inputs: list[dict[str, Any]],
) -> tuple[bool, bool, bool]:
    """
    Compare observed tool calls against the correct solution.
    Returns (correct_tool, correct_params, correct_request_body).
    """
    if not correct_solution:
        # No tool expected — correct if no tool was used
        correct_tool = len(tools_used) == 0
        return correct_tool, True, True

    expected_tools = [step["tool"] for step in correct_solution]
    observed_tools = [t["tool"] for t in tool_inputs]

    correct_tool = expected_tools == observed_tools

    correct_params = True
    correct_body = True

    for i, step in enumerate(correct_solution):
        expected_params = step.get("correct_query_params") or {}
        expected_body = step.get("correct_request_body")

        if i >= len(tool_inputs):
            correct_params = False
            correct_body = False
            break

        observed_args = tool_inputs[i].get("args", {})

        # Strip None values from expected params for comparison
        filtered_expected_params = {k: v for k, v in expected_params.items() if v is not None}
        filtered_observed_params = {k: v for k, v in observed_args.items() if k in filtered_expected_params}

        if filtered_observed_params != filtered_expected_params:
            correct_params = False

        if expected_body is not None:
            observed_body = observed_args.get("request_body") or observed_args.get("body")
            if observed_body != expected_body:
                correct_body = False

    return correct_tool, correct_params, correct_body


def save_to_db(
    prompt_id: str,
    prompt: str,
    category: str,
    difficulty: int,
    expected_outcome: str,
    correct_solution: list[dict],
    tools_used: list[str],
    tool_inputs: list[dict[str, Any]],
    duration_ms: int,
) -> None:
    correct_tool, correct_params, correct_body = evaluate_tool(
        correct_solution, tools_used, tool_inputs
    )

    # Extract expected fields from correct_solution
    expected_tools = [step["tool"] for step in correct_solution] if correct_solution else []
    expected_params = [step.get("correct_query_params") for step in correct_solution] if correct_solution else []
    expected_bodies = [step.get("correct_request_body") for step in correct_solution] if correct_solution else []

    observed_tools = [t["tool"] for t in tool_inputs]
    observed_params = [t["args"] for t in tool_inputs]

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        INSERT INTO interactions (
            interaction_id,
            prompt_id,
            prompt,
            category,
            difficulty,
            expected_outcome,
            expected_tool,
            expected_query_params,
            expected_request_body,
            observed_tool,
            observed_query_params,
            observed_request_body,
            correct_tool,
            correct_query_params,
            correct_request_body,
            duration_ms,
            timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()),
        prompt_id,
        prompt,
        category,
        difficulty,
        expected_outcome,
        json.dumps(expected_tools, ensure_ascii=False),
        json.dumps(expected_params, ensure_ascii=False),
        json.dumps(expected_bodies, ensure_ascii=False),
        json.dumps(observed_tools, ensure_ascii=False),
        json.dumps(observed_params, ensure_ascii=False),
        json.dumps([t.get("args", {}).get("request_body") for t in tool_inputs], ensure_ascii=False),
        int(correct_tool),
        int(correct_params),
        int(correct_body),
        duration_ms,
        datetime.utcnow().isoformat(),
    ))
    con.commit()
    con.close()


def get_prompts_from_json() -> list[dict]:
    with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


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
        try: 
            response = await anthropic_client.messages.create(
                model=model,
                max_tokens=4096,
                messages=messages,
                tools=claude_tools,
            )
        except anthropic.RateLimitError:
            print("Rate limit hit — waiting 60 seconds...")
            await asyncio.sleep(60)
            continue
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

                    print(
                        f"  ← Tool result: {result_text[:200]}"
                        f"{'...' if len(result_text) > 200 else ''}\n"
                    )

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
    init_db()

    anthropic_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    prompts = get_prompts_from_json()
    if TEST_PROMPT_ID:
        prompts = [p for p in prompts if p["id"] == TEST_PROMPT_ID]
    if not prompts:
        print("No prompts found in JSON.")
        return

    print(f"Found {len(prompts)} prompt(s) to run.\n")

    async with AsyncExitStack() as exit_stack:
        server_params = StdioServerParameters(
            command=r"C:\Code\KandidatExamensArbete\.venv\Scripts\python.exe",
            args=["server.py"],
            cwd=BASE_DIR,
            env=os.environ.copy(),
        )

        stdio_transport = await exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read, write = stdio_transport

        mcp_session = await exit_stack.enter_async_context(
            ClientSession(read, write)
        )

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

        for item in prompts:
            ref_id = item["id"]
            query = item["prompt"]
            correct_solution = item.get("correct_solution") or []

            print(f"--- Running prompt id={ref_id} ---")

            final_response, tools_used, tool_inputs, duration_ms = await run_query(
                anthropic_client,
                mcp_session,
                claude_tools,
                ANTHROPIC_MODEL,
                query,
            )

            save_to_db(
                prompt_id=ref_id,
                prompt=query,
                category=item.get("category", ""),
                difficulty=item.get("difficulty", 0),
                expected_outcome=item.get("expected_outcome", ""),
                correct_solution=correct_solution,
                tools_used=tools_used,
                tool_inputs=tool_inputs,
                duration_ms=duration_ms,
            )

            print(f"✓ Saved — {len(tools_used)} tool(s) used in {duration_ms}ms")


if __name__ == "__main__":
    asyncio.run(run_mcp_claude_client())