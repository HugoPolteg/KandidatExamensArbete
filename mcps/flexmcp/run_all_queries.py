import inspect
import server
from prompts import *
from pydantic import BaseModel

import inspect
from pydantic import BaseModel


def build_kwargs(func, query_params, request_body):
    sig = inspect.signature(func)
    kwargs = {}

    for name, param in sig.parameters.items():
        annotation = param.annotation

        # --- Pydantic models ---
        if inspect.isclass(annotation) and issubclass(annotation, BaseModel):

            # Heuristik: body vs query
            if name.lower() in ["body", "data", "payload"]:
                if request_body:
                    kwargs[name] = annotation(**request_body)

            elif name.lower() in ["query", "params"]:
                if query_params:
                    kwargs[name] = annotation(**query_params)

            else:
                # fallback (för edge cases)
                if request_body:
                    kwargs[name] = annotation(**request_body)
                elif query_params:
                    kwargs[name] = annotation(**query_params)

        # --- vanliga parametrar ---
        else:
            if name in query_params:
                kwargs[name] = query_params[name]

    return kwargs


def run_all_queries(data, server):
    for item in data:
        print(f"\n=== Running {item['id']} ===")

        tool_chain = item.get("correct_solution", [])

        for step in tool_chain:
            tool_name = step["tool"]
            query_params = step.get("query_params") or step.get("correct_query_params") or {}
            request_body = step.get("request_body") or step.get("correct_request_body") or {}

            print(f"\n-> Tool: {tool_name}")

            func = getattr(server, tool_name, None)
            if func is None:
                print(f"ERROR: Function '{tool_name}' not found")
                continue

            # remove None
            query_params = {k: v for k, v in query_params.items() if v is not None}

            try:
                kwargs = build_kwargs(func, query_params, request_body)

                print("KWARGS:")
                for k, v in kwargs.items():
                    print(f"  {k}: {type(v)}")

                result = func(**kwargs)

                print("Result:")
                print(result)

            except Exception as e:
                print("ERROR:", e)

run_all_queries(data, server)