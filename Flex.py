from mcp.server.fastmcp import FastMCP
import requests
from typing import TypedDict, Optional

mcp = FastMCP("Flex")

BASE_URL = "https://stage-api.flexhrm.com"


class Entry(TypedDict):
    start_time: str
    end_time: str
    time_code: str
    billable: Optional[bool]
    comment: Optional[str]

@mcp.tool()
def dagredovisning(employeeId :str, date: list[str], entries:list[Entry]) -> dict:
    """
    Create or update one or more time reports for an employee on one or more given dates.

    Args:
        employeeId: UUDI of the employee.
        date: ISO date string (e.g. 2026-03-23)
        entries: 
            Each entrie must include:      
                start_time: Time of day for which the user started work (HH:MM)
                end_time: Time of day for which the user finished work (HH:MM)
            Each entire can (but must not) also include
                billable: Wheater or not the work was billable
                comment: Comments the user whiches to append to their time report
        
    Returns:
        API response JSON
        """

    time_rows = []
    for e in entries:
        row = {
            "billable": e.billable,
            "externalComment": e.comment,
            "timeCode": {"code": e.time_code},
            "fromTimeDateTime": f"{date}T{e.start_time}:00Z",
            "toTimeDateTime": f"{date}T{e.end_time}:00Z"
        }
        time_rows.append(row)

    payload = {"timeRows": time_rows}
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