from mcp.server.fastmcp import FastMCP
import requests
from pydantic import BaseModel  
from uuid import UUID
from datetime import date, time
from typing import Dict


mcp = FastMCP("Flex")

BASE_URL = "https://stage-api.flexhrm.com"

class DagsEntry(BaseModel):
    employee_id: UUID
    date: date
    start_time: time
    end_time: time
    time_code: str
    billable: bool = True
    comment: str = ""

@mcp.tool()
def update_salary_by_id(salary_id: UUID, salary_data: Dict) -> dict:
    """
    Updates a salary by id

    Args:
        Required:
            salary_id: (UUID, required) UUID of the salary.
            salary_data: (dict, required) JSON body containing the updated salary information.
    """

    url = f"{BASE_URL}/api/salaries/{salary_id}"

    response = requests.put(url, json=salary_data)

    response.raise_for_status()

    return response.json()

@mcp.tool()
def get_salary_by_id(salary_id: UUID) -> dict:
    """
    Gets a salary by id

    Args:
        Required:
            salary_id: (UUID, required) UUID of the salary.
    """

    url = f"{BASE_URL}/api/salaries/{salary_id}"

    response = requests.get(url)

    response.raise_for_status()

    return response.json()

@mcp.tool()
def get_time_report_by_employee(employee_id: UUID, date: date = None, generated: bool = True) -> dict:
    """
    Gets a time report for an employee

    Args:
        Required:
            employee_id: (UUID, required) UUID of the employee.
        Optional:
            date: (ISO date, optional) date of the time report
            generated: (bool, optional) include generated time rows
    """

    url = f"{BASE_URL}/api/employees/{employee_id}/timereport"

    params = {
        "generated": generated
    }

    if date:
        params["date"] = date.isoformat()

    response = requests.get(url, params=params)

    response.raise_for_status()

    return response.json()

@mcp.tool()
def put_time_report(entries:list[DagsEntry]) -> dict:
    """
    Create or update one or more time reports for an employee on one or more given dates.

    Args:
        entries: a list of entries 
            Each entry must include: 
                employee_id: (UUID, required) UUDI of the employee.
                date: (ISO date, required) date of the time report
                start_time: (HH:MM, required) Time of day for which the user started work
                end_time: (HH:MM, required) Time of day for which the user finished work
            Each entry can (but must not) also include:
                billable: (bool, optional) Whether or not the work was billable
                comment: (str, optional)
        
    Returns:
        API response JSON
        """
    results =[]
    grouped = {}
    e:DagsEntry

    for e in entries:
        key = (str(e.employee_id), e.date.isoformat())
        grouped.setdefault(key, []).append(e)
   
    
    for (employee_id, date_str), group_entries in grouped.items():

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
            url=f"{BASE_URL}/api/employees/{employee_id}/timereports/{date_str}",
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