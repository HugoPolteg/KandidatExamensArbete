from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("Flex")

BASE_URL = "https://stage-api.flexhrm.com"

@mcp.tool()
def dagredovisning(employeeId :str, date: str, payload: dict) -> dict:
    """
    Create or update a time report for an employee on a given date.

    Args:
        employeeId (str): UUDI of the employee.
        date (str): ISO date string (e.g. 2026-03-23)
        payload (dict): JSON body for the time report

    Returns:
        API response JSON
        """
    
    url = f"{BASE_URL}/api/employees/{employeeId}/timereports/{date}"
    try:
        response = requests.put(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        response.raise_for_status

    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json() if response.content else {"status": "ok"}

if __name__ == "__main__":
    mcp.run()