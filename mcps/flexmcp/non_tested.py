import inspect
import re
import server  # din server-fil

# 1. Hämta alla funktioner i server
server_functions = {
    name for name, obj in inspect.getmembers(server, inspect.isfunction)
}
for t in server_functions:
    if len(t) > 64:
        print(t)