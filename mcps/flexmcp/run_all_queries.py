import inspect
import server
from prompts import *
from pydantic import BaseModel

def get_pydantic_param(sig):
    """Return (param_name, model_class) for the first Pydantic model param, or (None, None)."""
    for param_name, param in sig.parameters.items():
        annotation = param.annotation
        if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
            return param_name, annotation
    return None, None

def run_all_queries(data, server):
    for item in data:
        print(f"\n=== Running {item['id']} ===")

        tool_chain = item.get("tool_chain", [])
        
        for step in tool_chain:
            tool_name = step["tool"]
            query_params = step.get("query_params") or {}
            request_body = step.get("request_body") or step.get("correct_request_body")


            print(f"\n-> Tool: {tool_name}")

            func = getattr(server, tool_name, None)

            if func is None:
                print(f"ERROR: Function '{tool_name}' not found on server")
                continue

            clean_params = {k: v for k, v in query_params.items() if v is not None}

            try:
                sig = inspect.signature(func)
                for param_name, param in sig.parameters.items():
                    print(f"  param: {param_name}, annotation: {param.annotation}, default: {param.default}")
                pydantic_param, model_class = get_pydantic_param(sig)

                if pydantic_param and request_body:
                    print(f"Calling with Pydantic model body + params")
                    model_instance = model_class(**request_body)
                    result = func(**clean_params, **{pydantic_param: model_instance})

                elif pydantic_param and clean_params:
                    # Body fields passed as flat query params — wrap them into the model
                    print(f"Calling with Pydantic model built from query params")
                    model_instance = model_class(**clean_params)
                    result = func(**{pydantic_param: model_instance})

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