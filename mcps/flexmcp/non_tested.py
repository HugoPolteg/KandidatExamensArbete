import inspect
import re
import server  # din server-fil

# 1. Hämta alla funktioner i server
server_functions = {
    name for name, obj in inspect.getmembers(server, inspect.isfunction)
}

# 2. Läs testfilen som text
with open("working_funcs.py", "r", encoding="utf-8") as f:
    test_code = f.read()

# 3. Extrahera alla anrop till server.<funktion>
tested_functions = set(re.findall(r"server\.(\w+)\(", test_code))

# 4. Ta fram de som saknas
untested_functions = server_functions - tested_functions

# 5. Skriv ut resultat
print("Funktioner som INTE testas:\n")
for func in sorted(untested_functions):
    print(func)