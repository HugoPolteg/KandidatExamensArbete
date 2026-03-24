from mcp.server.fastmcp import FastMCP
import requests
from pydantic import BaseModel  
from uuid import UUID
from datetime import date, time

mcp = FastMCP("Flex")

BASE_URL = "https://stage-api.flexhrm.com"


class DagsEntry(BaseModel):
    employeeId: UUID
    date: date
    start_time: time
    end_time: time
    time_code: str
    billable: bool = True
    comment: str = ""

@mcp.tool()
def dagredovisning(entries:list[DagsEntry]) -> dict:
    """
    Create or update one or more time reports for an employee on one or more given dates.

    Args:
        entries: a list of entries 
            Each entrie must include: 
            employeeId: UUDI of the employee.
            date: ISO date string (e.g. 2026-03-23)  
                start_time: Time of day for which the user started work (HH:MM)
                end_time: Time of day for which the user finished work (HH:MM)
            Each entire can (but must not) also include
                billable: Wheater or not the work was billable
                comment: Comments the user whiches to append to their time report
        
    Returns:
        API response JSON
        """
    results =[]
    grouped = {}



    for e in entries:
        e: DagsEntry
        key = (str(e.employeeId), e.date.isoformat())
        grouped.setdefault(key, []).append(e)
   
    
    for (employeeId, date_str), group_entries in grouped.items():

        time_rows = []

        for e in group_entries:
            from_dt = f"{e.date.isoformat()}T{e.start_time.strftime('%H:%M:%S')}Z"
            to_dt = f"{e.date.isoformat()}T{e.end_time.strftime('%H:%M:%S')}Z"

            row = {
                "billable": e.billable,
                "externalComment": e.comment,
                "timeCode": {"code": e.time_code},
                "fromTimeDateTime": from_dt,
                "toTimeDateTime": to_dt
            }

            time_rows.append(row)

    payload = {"timeRows": time_rows}

    try:
        response = requests.put(
            url=f"{BASE_URL}/api/employees/{employeeId}/timereports/{date_str}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        response.raise_for_status()
        results.append(response.json() if response.content else {"status": "ok"})

    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return {"results": results}

if __name__ == "__main__":
    mcp.run()