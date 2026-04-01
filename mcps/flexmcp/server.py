from mcp.server.fastmcp import FastMCP
import requests

from pydantic import Field
from uuid import UUID
from datetime import date, datetime
from typing import Optional
from models import DayEntry,TimeRow, ProjectModel, GetSalaries, GetSalariesByCompany, GetSalariesByCompanyAndEmployee, GetSalariesByEmployee, UpdateOrCreateSalaries, GetAllSalaries, StampingAccountModel
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


#@mcp.tool()
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
def delete_salary(
    salary_id: UUID = Field(..., description="UUID of the salary"),
) -> dict:
    """
    Deletes a salary by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/salaries/{salary_id}"

    try:
        response = requests.delete(
            url, 
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()

@mcp.tool()
def get_salaries(
    query: GetSalaries = Field(..., 
    description="Full query object. Instance is required. All other fields are optional")
    ) -> dict:
    """
     Get salaries for a given instance.

    Returns:
        A JSON dict containing the list of salaries.
    """
    url = f"{consts.API_ENDPOINT}/api/instance/{query.instance}/salaries"

    params = query.model_dump(by_alias=True, exclude_none=True, exclude={"instance"})

    try:
        response = requests.get(
            url, 
            params=params, 
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()
@mcp.tool()

@mcp.tool()
def get_salaries_by_company(
    query: GetSalariesByCompany = Field(..., 
    description="Full query object. Instance and company_id are required. All other fields are optional")
    ) -> dict:
    """
     Get salaries for a given company

    Returns:
        A JSON dict containing the list of salaries.
     """
    url = f"{consts.API_ENDPOINT}/api/instance/{query.instance}/company/{query.company_id}/salaries"

    params = query.model_dump(by_alias=True, exclude_none=True, exclude={"instance", "company_id"})

    try:
        response = requests.get(
            url, 
            params=params, 
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()
 
@mcp.tool()
def get_salaries_by_company_and_employee(
    query: GetSalariesByCompanyAndEmployee = Field(...,
    description="Full query object. Instance, company_id and employee_id are required. All other fields are optional")
    )-> dict:
    """
     Get salaries for an employee in a given company

    Returns:
        A JSON dict containing the list of salaries.
     """
    
    url = f"{consts.API_ENDPOINT}/api/instance/{query.instance}/company/{query.company_id}/employee/{query.employee_id}/salaries"

    params = query.model_dump(by_alias=True, exclude_none=True, exclude={"instance", "company_id", "employee_id"})

    try:
        response = requests.get(
            url, 
            params=params, 
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}") 
    return response.json()

@mcp.tool()
def get_salaries_by_employee(
    query: GetSalariesByEmployee = Field(..., description="Full query object. Instance and employee_id are required. All other fields are optional")
    ) -> dict:
    """
     Get salaries for an employee

     Returns: 
        A JSON dict containing the list of salaries.
    """
    url = f"{consts.API_ENDPOINT}/api/instance/{query.instance}/employee/{query.employee_id}/salaries"

    params = query.model_dump(by_alias=True, exclude_none=True, exclude={"instance", "employee_id"})

    try:
        response = requests.get(
            url, 
            params=params, 
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

#@mcp.tool()
def update_salaries_by_employee(
    query: UpdateOrCreateSalaries = Field(..., description="Full query object. Instance, employee_id, and company_id are required. All other fields are optional")
    ) -> dict:
    """
     Update salaries for an employee in a given company. 

     Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/employees/{query.employee_id}/salaries"

    payload = query.model_dump(by_alias=True, exclude_none=True)

    try:
        response = requests.put(
            url, 
            params={"employeeId": query.employee_id},
            json=payload, 
            headers={"Content-Type": "application/json"},
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_all_salaries(
    query: GetAllSalaries = Field(..., description="Full query object. All fields are optional")
    ) -> dict:
    """
     Get salaries.
     """
    url = f"{consts.API_ENDPOINT}/api/salaries"

    params = query.model_dump(by_alias=True, exclude_none=True)

    try:
        response = requests.get(
            url, 
            params=params, 
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

#@mcp.tool()
def create_salary(
    query: UpdateOrCreateSalaries = Field(..., description="Full query object. Instance, employee_id, and company_id are required. All other fields are optional")
    ) -> dict:
    """
     Create a salary for an employee in a given company. 

     Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/salaries"

    payload = query.model_dump(by_alias=True, exclude_none=True)

    try:        
        response = requests.post(
            url, 
            json=payload, 
            headers={"Content-Type": "application/json"},
            timeout=consts.API_TIMEOUT
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
def get_employee(
    employee_id: UUID = Field(..., description="Employee ID"),
) -> dict:
    """
    Gets employee information by ID

    Returns:
        Employee data as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/employees/{employee_id}"

    try:
        response = requests.get(url, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()

#@mcp.tool()
def put_time_report(
    employee_id: UUID = Field(..., description="Employee ID"),
    date: datetime = Field(..., description="Date of the report"),
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
def get_employment_periods_by_employee(
    employee_id: UUID = Field(..., description="Employee ID"),
    domain_name: Optional[str] = Field(None, description="Domain name."),
    company_id: Optional[UUID] = Field(None, description="Company id."),
    company_number: Optional[int] = Field(None, "Company number."),
    employment_number: Optional[int] = Field(None, "Employment number."),
    page_index: Optional[int] = Field(0, description="Page index for search. Begins at 0."),
    page_size: Optional[int] = Field(20, description="Number of entries per page.")
) -> dict:
    """
    Gets a list of employment periods by employee id.

    Returns:
        The employment periods from and to dates, id of resignation cause and type of employment.
    """

@mcp.tool()
def get_companies(
    domain_name: str = Field(..., description="Domain name."),
    start_range: int = Field(..., description="Start range of company numbers:s."),
    end_range: int = Field(..., description="End range of the company numbers:s.")
) -> dict:
    """
    Gets a list of companies.

    Returns:
        The company names, numbers and customer instances within the range.
    """
    url = f"{consts.API_ENDPOINT}/GetCompanyInformation/GetCompanyInformation"
    params = {"instance": domain_name, "startRange": start_range, "endRange": end_range}
    try:
        response = requests.get(url, params=params, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()


@mcp.tool()
def get_instances(
    instance_name: Optional[str] = Field(None, description="Instance name."),
    domain: Optional[str] = Field(None, description="Domain name."),
    page_index: Optional[int] = Field(0, description="Page index for search. Begins at 0."),
    page_size: Optional[int] = Field(20, description="Number of entries per page.")
) -> dict:
    """Gets a list of instances. Optional to specify name, domain and page information."""
    url = f"{consts.API_ENDPOINT}/api/instances"

    parameters = {"pageIndex": page_index, "pageSize": page_size}
    if instance_name is not None:
        parameters["name"] = instance_name
    if domain is not None:
        parameters["domain"] = domain
    try:
        response = requests.get(url, parameters=parameters, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()

@mcp.tool()
def get_time_groups(
    company_number: Optional[int] = Field(None, "Company number."),
    time_group_code: Optional[str] = Field(None, "Time group code."),
    page_index: Optional[int] = Field(0, "Page index for search. Begins at 0."),
    page_size: Optional[int] = Field(20, "Number of entries per page.")
) -> dict:
    """Gets a list of time groups. Optional to specify search parameters."""
    url = f"{consts.API_ENDPOINT}/api/instances"

    parameters = {"companynumber": company_number, "code": time_group_code, "pageIndex": page_index, "pageSize": page_size}
    try:
        response = requests.get(url, parameters=parameters, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()

@mcp.tool()
def get_company(
    company_id: UUID = Field(..., description="UUID of the company.")
    ) -> dict:
    """
    Gets company information by id.

    Returns:
        The detailed company information as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/companies/{company_id}"

    try:
        response = requests.get(url, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()


@mcp.tool()
def get_project(
    project_id: UUID = Field(..., description="UUID of the project.")
) -> dict:
    """
    Gets project information by ID

    Returns:
        Project data as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/employees/{project_id}"

    try:
        response = requests.get(url, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()


 
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


#@mcp.tool()
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


#@mcp.tool()
def update_project(
    project_id: UUID = Field(..., description="UUID of the project."),
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

#@mcp.tool()
def stamping_by_Id  (
    userId: UUID = Field(..., description="UUID of the employee."),
    internal_comment: Optional[str] = Field(None, max_length=2000, description="Internal comment for the stamping. Nullable."),
    date_time: Optional[datetime] = Field(None, description="Date and time of the stamping in ISO format."),
    account: StampingAccountModel = Field(..., description="Stamping account details including account code and distribution ID, both required."),
    ) -> dict:
    """
    Stamps in or out for a user

    Returns:
        API response as a JSON dict.
    """

    url = f"{consts.API_ENDPOINT}/api/stamping/{userId}/inOut"

    params = {}
    if internal_comment is not None:
        params["internalComment"] = internal_comment
    if date_time is not None:
        params["dateTime"] = date_time.isoformat()

    payload = account.model_dump(by_alias=True, exclude_none=True)

    try:
        response = requests.post(
            url, 
            
            json=payload, 
            headers={"Content-Type": "application/json"},
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

#@mcp.tool()
def stamping_by_employeeId(
    employeeId: UUID = Field(..., description="UUID of the employee."),
    internal_comment: Optional[str] = Field(None, max_length=2000, description="Internal comment for the stamping. Nullable."),
    date_time: Optional[datetime] = Field(None, description="Date and time of the stamping in ISO format."),
    account: StampingAccountModel = Field(..., description="Stamping account details including account code and distribution ID, both required."),
    )-> dict:
    """
    Stamps in or out for an employee by their ID

    Returns:
        API response as a JSON dict.

    """
    url = f"{consts.API_ENDPOINT}/api/employees/{employeeId}/inOut"

    params = {}
    if internal_comment is not None:
        params["internalComment"] = internal_comment
    if date_time is not None:
        params["dateTime"] = date_time.isoformat()

    payload = account.model_dump(by_alias=True, exclude_none=True)

    try:
        response = requests.post(
            url, 
            json=payload, 
            headers={"Content-Type": "application/json"},
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_stamping_by_userID(
    user_id: UUID = Field(..., description="UUID of the employee."),
    date_time: Optional[datetime] = Field(None, description="Date and time for which to retrieve stamping information, in ISO format.")
    )-> dict:
    """
    Gets stamping information for a user

    Response:
        A JSON dict containing stamping details for the specified user.
     """
    
    url = f"{consts.API_ENDPOINT}/api/stamping/{user_id}/timeRows"

    params = {}
    if date_time is not None:
        params["dateTime"] = date_time.isoformat()
    try:
        response = requests.get(
        url, 
        params=params, 
        timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

if __name__ == "__main__":
    mcp.run()


