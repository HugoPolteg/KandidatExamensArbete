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

        query = """🧪 Adversarial Data Generation Prompt

You are responsible for seeding a project management system via API calls. Your goal is to create a complex, inconsistent, and edge-case-heavy dataset that will stress-test downstream automation.

You must intentionally introduce ambiguity, imbalance, and inconsistencies while still respecting API schemas.

1. Create Multiple Projects
Create 5–8 projects with:
Varying numbers of members (some empty, some large)
Overlapping names and similar descriptions (to confuse selection logic)
Mixed configurations (some with triage enabled, some without)
2. Populate Workspaces & Sprints

For each project:

Use at least 2 workspaces (implicit via sprints/cards)
Create 5–12 sprints per workspace with:
Irregular durations (1 day → 45 days)
Overlapping date ranges
Gaps in timelines (especially within last 90 days)
Some sprints with missing or misleading descriptions
Randomly closed and open states inconsistent with dates
3. Create Cards (Highly Skewed Distribution)
Create 100–300 cards per project with:
Highly uneven assignment:
Some users have 0 cards
Some users have 10+ cards
Many cards with:
No assignee
Multiple assignees
Random priorities, with many missing
Mixed states (open/closed) not matching sprint/epic progress
Some cards not assigned to any sprint
Some cards assigned to non-recent or closed sprints
4. Create Epics with Inconsistencies
Create 10–25 epics per project
For each epic:
Attach a random subset of cards (including none for some epics)
Ensure:
Some epics are "open" but mostly completed
Some are "completed" but contain open cards
Some epics have no cards at all
Randomize:
status vs state mismatches (e.g., state="open", status="completed")
Leave some epics without epic lists
5. Epic Lists Chaos
For some projects:
Create multiple epic lists with unclear ordering
For others:
Create no epic lists at all
Randomly:
Assign some epics to lists
Leave others unassigned
Duplicate or near-duplicate list names
6. Triage & Card Placement Issues
Ensure:
Many cards are left in triage
Some high-priority cards are in backlog
Some low-priority cards are in active sprints
Move cards into inconsistent categories:
Same category names across different workspaces
Slight variations in naming ("Backlog", "backlog", "BACKLOG")
7. Customers & Activity Gaps
Add 5–15 customers per project
Ensure:
Some customers are linked to nothing
Some linked only to inactive/closed epics
Some heavily overrepresented
Do NOT clearly indicate relationships — force inference
8. Events & Comments Noise
Add comments and events such that:
Some low-priority cards have lots of activity
Some high-priority cards have none
Event timelines contradict states (e.g., recent activity on "closed" items)
9. Subtle Edge Cases

Introduce:

Cards referencing:
Deleted or non-existent epics (if possible within constraints)
Epics reordered inconsistently
Sparse but critical metadata (e.g., missing descriptions where needed most)
Date anomalies:
Future-dated sprints
Cards created after sprint end dates
10. Constraints
You must:
Respect all required fields in API schemas
Avoid outright API errors (data must be accepted)
You should:
Maximize ambiguity
Maximize conflicting signals
Avoid clean or balanced distributions
🎯 Goal

The final dataset should:

Make it difficult to determine the “correct” project
Require non-trivial inference across entities
Contain conflicting signals that force trade-offs
Break naive assumptions (e.g., "closed sprint ⇒ completed work")"""
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