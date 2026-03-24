import asyncio
import os
from contextlib import AsyncExitStack
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import AsyncAnthropic

load_dotenv()





async def run_mcp_claude_client():

    #CONFIG
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL = "claude-3-5-haiku-20241022"
    anthropic_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    async with AsyncExitStack() as exit_stack:

        server_params = StdioServerParameters(
            command="node", 
            args=["C:\\Code\\KandidatExamensArbete\\zube.js"], 
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
        
        response = await anthropic_client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1000,
            messages=[{"role": "user", "content": query}],
            tools=claude_tools
        )

        messages = [{"role": "user", "content": query}]

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_args = block.input
                    
                    print(f"Claude is calling tool: {tool_name}")
                    result = await mcp_session.call_tool(tool_name, tool_args)
                    
                    result_text = str(result.content)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_text
                    })
            messages.append({"role": "user", "content": tool_results})

            final_response = await anthropic_client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=1000,
                messages=messages,
                tools=claude_tools
            )

            print("\nClaude's Response:")
            print(final_response.content[0].text)

if __name__ == "__main__":
    asyncio.run(run_mcp_claude_client())
