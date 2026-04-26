import inspect
import server
from prompts import *

def run_all_queries(data, server):
    for item in data:
        print(f"\n=== Running {item['id']} ===")

        tool_chain = item.get("tool_chain", [])
        
        for step in tool_chain:
            tool_name = step["tool"]
            query_params = step.get("query_params") or {}
            request_body = step.get("request_body")

            print(f"\n-> Tool: {tool_name}")

            func = getattr(server, tool_name, None)

            if func is None:
                print(f"ERROR: Function '{tool_name}' not found on server")
                continue

            clean_params = {
                k: v for k, v in query_params.items() if v is not None
            }

            try:
                sig = inspect.signature(func)

                if request_body:
                    print(f"Calling with body + params")

                    result = func(
                        **clean_params,
                        body=request_body 
                    )
                else:
                    print(f"Calling with params only")

                    result = func(**clean_params)

                print("Result:")
                print(result)

            except TypeError as e:
                print("TypeError:", e)

            except Exception as e:
                print("Unhandled error:", e)

run_all_queries(data, server)