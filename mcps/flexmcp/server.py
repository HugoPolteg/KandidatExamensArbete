from mcp.server.fastmcp import FastMCP
import requests

from pydantic import Field
from uuid import UUID
from datetime import date, datetime
from typing import Optional
from models import DayEntry, TimeRow, ProjectModel
import consts

mcp = FastMCP("Flex")

def to_api_time_row(row: TimeRow) -> dict:
    return {
        "fromTimeDateTime": row.start.isoformat(),
        "toTimeDateTime": row.end.isoformat(),
        "billed": row.billable,
        "externalComment": row.comment,
        "timeCode": {"code": row.time_code} if row.time_code else None,
    }

@mcp.tool()
def get_salary_by_id(
    salary_id: UUID = Field(..., description="UUID of the salary."),
) -> dict:
    """
    Gets a salary by id.

    Returns:
        Salary data as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/salaries/{salary_id}"

    try:
        response = requests.get(url, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()


@mcp.tool()
def update_salary_by_id(
    salary_id: UUID = Field(..., description="UUID of the salary."),
    salary_data: dict = Field(..., description="JSON body containing the updated salary fields."),
) -> dict:
    """
    Updates a salary by id.

    Returns:
        Updated salary data as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/salaries/{salary_id}"

    try:
        response = requests.put(
            url,
            json=salary_data,
            headers={"Content-Type": "application/json"},
            timeout=consts.API_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()


@mcp.tool()
def get_time_report_by_employee(
    employee_id: UUID = Field(..., description="UUID of the employee."),
    report_date: Optional[date] = Field(None, description="Date of the time report (YYYY-MM-DD). Defaults to today if omitted."),
    generated: Optional[bool] = Field(True, description="Whether to include generated time rows. Defaults to True."),
) -> dict:
    """
    Gets a time report for an employee.

    Returns:
        Time report data as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/employees/{employee_id}/timereport"

    params = {}
    if report_date is not None:
        params["date"] = report_date.isoformat()
    if generated is not None:
        params["generated"] = generated

    try:
        response = requests.get(url, params=params, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()


@mcp.tool()
def put_time_report(
    employee_id: UUID = Field(..., description="Employee ID (path parameter)"),
    date: datetime = Field(..., description="Date of the report (path parameter)"),
    entry: DayEntry = Field(..., description="Time report payload for the given day"),
) -> dict:
    """
    Create or replace a full time report day for a specific employee and date.

    This replaces ALL existing entries for that day.

    Returns:
        API response as dict.
    """

    # Convert model to API payload using aliases
    payload = entry.model_dump(by_alias=True, exclude_none=True)

    try:
        response = requests.put(
            url=f"{consts.API_ENDPOINT}/api/employees/{employee_id}/timereports/{date.isoformat()}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=consts.API_TIMEOUT,
        )
        response.raise_for_status()

        return response.json() if response.content else {"status": "ok"}

    except requests.RequestException as e:
        raise RuntimeError(
            f"API request failed for employee {employee_id} on {date}: {e}"
        )

@mcp.tool()
def insert_time_row(
    employee_id: UUID = Field(..., description="UUID of the employee."),
    row_date: date = Field(..., description="Date of the time row (YYYY-MM-DD)."),
    time_row: TimeRow = Field(
        ...,
        description=(
            "Time row data. Must include start and end times. All other fields are optional."
        ),
    ),
) -> dict:
    """
    Inserts a time row for an employee on a specific date.
    Overlapping rows are automatically split to accommodate the new entry.
    If timeCode is omitted, the employee's default work time code is used.
    Accounting entries are populated automatically based on system rules.
 
    Returns:
        The created time row as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/employees/{employee_id}/timerow/{row_date.isoformat()}"
 
    payload = to_api_time_row(time_row)
 
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=consts.API_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed for employee {employee_id} on {row_date}: {e}")
 
    return response.json() if response.content else {"status": "ok"}
 
@mcp.tool()
def get_schedule_days_by_employee(
    employee_id: UUID = Field(..., description="UUID of the employee."),
    from_date: Optional[date] = Field(None, description="Start of the date range (YYYY-MM-DD). Inclusive."),
    to_date: Optional[date] = Field(None, description="End of the date range (YYYY-MM-DD). Inclusive."),
    hide_workshifts: Optional[bool] = Field(
        False,
        description=(
            "If True, the workshifts list on each schedule day will be empty. "
            "Use to minimize response size when shift details are not needed. Defaults to False."
        ),
    ),
) -> list:
    """
    Gets schedule days for an employee, optionally filtered by date range.
    Each schedule day includes hours, deviation info, week number, working hours,
    and optionally a list of work shifts with account and break details.
 
    Returns:
        List of schedule day objects as JSON.
    """
    url = f"{consts.API_ENDPOINT}/api/employees/{employee_id}/scheduledays"
 
    params = {}
    if from_date is not None:
        params["fromDate"] = from_date.isoformat()
    if to_date is not None:
        params["toDate"] = to_date.isoformat()
    if hide_workshifts is not None:
        params["hideWorkshifts"] = hide_workshifts
 
    try:
        response = requests.get(url, params=params, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed for employee {employee_id}: {e}")
 
    return response.json()


@mcp.tool()
def update_project(
    project_id: UUID = Field(..., description="UUID of the project to update."),
    project: ProjectModel = Field(
        ...,
        description=(
            "Full project object. code and name are required. All other fields are optional "
            "and only sent if explicitly provided. Enum fields are integers — see field "
            "descriptions for valid values."
        ),
    ),
) -> dict:
    """
    Updates a project by id.
    The request body must include code and name at minimum.
    All other fields are optional and will only be included in the payload if set.
 
    Returns:
        Updated project data as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/projects/{project_id}"
 
    payload = project.model_dump(by_alias=True, exclude_none=True)
 
    try:
        response = requests.put(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=consts.API_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed for project {project_id}: {e}")
 
    return response.json() if response.content else {"status": "ok"}

if __name__ == "__main__":
    mcp.run()