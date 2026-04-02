from mcp.server.fastmcp import FastMCP
import requests
from pydantic import Field
from uuid import UUID
from datetime import date, datetime
from typing import Optional
from models import DayEntry,TimeRow, ProjectModel, GetSalaries, GetSalariesByCompany,\
GetSalariesByCompanyAndEmployee, GetSalariesByEmployee, UpdateOrCreateSalaries, \
GetAllSalaries, StampingAccountModel, Union, GetUsers, GetVehicleType, GetVehicleTypeByCompanyId, \
VehicleTypeRequestModel, GetTravelClaims, GetUsersByInstance, ListCompaniesInput
import consts
from dotenv import load_dotenv
import os
import base64
load_dotenv()
DOMAIN = os.getenv("DOMAIN")
INSTANCE = os.getenv("INSTANCE")
s = requests.Session()
s.headers.update({
    "Content-Type": "application/json",
    "Instance": DOMAIN,
    "Authorization": 'Basic ' + DOMAIN + ":" + os.getenv("FLEX_USERNAME") + ":" + os.getenv("FLEX_PASSWORD")
})
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
        response = s.get(url, timeout=consts.API_TIMEOUT)
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
        response = s.put(
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
        response = s.delete(
            url, 
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()

@mcp.tool()
def get_salaries_by_instance(
    query: GetSalaries = Field(..., 
    description="Full query object, all fields are optional")
    ) -> dict:
    """
     Get salaries for a given instance. If no instance is provided, defaults to the default-domain instance.

    Returns:
        A JSON dict containing the list of salaries.
    """
    url = f"{consts.API_ENDPOINT}/api/instance/{query.instance}/salaries"

    params = query.model_dump(by_alias=True, exclude_none=True, exclude={"instance"})

    try:
        response = s.get(
            url, 
            params=params, 
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()

@mcp.tool()
def get_salaries_by_company(
    query: GetSalariesByCompany = Field(..., 
    description="Full query object. company_id is required. All other fields are optional")
    ) -> dict:
    """
     Get salaries for a given company and instance. If no instance is provided, defaults to the default-domain instance.

    Returns:
        A JSON dict containing the list of salaries.
     """
    url = f"{consts.API_ENDPOINT}/api/instance/{query.instance}/company/{query.company_id}/salaries"

    params = query.model_dump(by_alias=True, exclude_none=True, exclude={"instance", "company_id"})

    try:
        response = s.get(
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
    description="Full query object. Company_id and employee_id are required. All other fields are optional")
    )-> dict:
    """
     Get salaries for an employee of a given company in a given instance. If no instance is provided, defaults to the default-domain instance.

    Returns:
        A JSON dict containing the list of salaries.
     """
    
    url = f"{consts.API_ENDPOINT}/api/instance/{query.instance}/company/{query.company_id}/employee/{query.employee_id}/salaries"

    params = query.model_dump(by_alias=True, exclude_none=True, exclude={"instance", "company_id", "employee_id"})

    try:
        response = s.get(
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
    query: GetSalariesByEmployee = Field(..., description="Full query object. Employee_id is required. All other fields are optional")
    ) -> dict:
    """
     Get salaries for an employee in a given instance. If no instance is provided, defaults to the default-domain instance.

     Returns: 
        A JSON dict containing the list of salaries.
    """
    url = f"{consts.API_ENDPOINT}/api/employee/{query.employee_id}/salaries"

    params = query.model_dump(by_alias=True, exclude_none=True, exclude={"employee_id"})

    try:
        response = s.get(
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
    query: UpdateOrCreateSalaries = Field(..., description="Full query object. Employee_id, and company_id are required. All other fields are optional")
    ) -> dict:
    """
     Update salaries for an employee of a given company for a given isntance-id. If no instanceid is provided, uses default instance-id. 

     Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/employees/{query.employee_id}/salaries"

    payload = query.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.put(
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
        response = s.get(
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
    query: UpdateOrCreateSalaries = Field(..., description="Full query object. Employee_id, and company_id are required. All other fields are optional")
    ) -> dict:
    """
     Create a salary for an employee of a given company for a given instance-id. If no instance id is provided, uses default instance-id. 

     Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/salaries"

    payload = query.model_dump(by_alias=True, exclude_none=True)

    try:        
        response = s.post(
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
        response = s.get(url, params=params, timeout=consts.API_TIMEOUT)
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
        response = s.get(url, timeout=consts.API_TIMEOUT)
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
        response = s.put(
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
    company_number: Optional[int] = Field(None, description="Company number."),
    employment_number: Optional[int] = Field(None, description="Employment number."),
    page_index: Optional[int] = Field(0, description="Page index for search. Begins at 0."),
    page_size: Optional[int] = Field(20, description="Number of entries per page.")
) -> dict:
    """
    Gets a list of employment periods by employee id.

    Returns:
        The employment periods from and to dates, id of resignation cause and type of employment.
    """
    url = f"/api/employees/{employee_id}/employmentperiods"
    params = {"pageIndex": page_index, "pageSize": page_size}
    if domain_name is not None:
        params["instance"] = domain_name
    if company_id is not None:
        params["companyId"] = company_id
    if company_number is not None:
        params["companynumber"] = company_number
    if employment_number is not None:
        params["employmentnumber"] = employment_number

    try:
        response = s.get(url, params=params, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()

@mcp.tool()
def list_all_companies(
    params: ListCompaniesInput = ListCompaniesInput()
) -> dict:
    """
    Gets a list of companies.

    Returns:
        The company names, numbers and customer instances within the range.
    """
    url = f"{consts.API_ENDPOINT}/instance/{params.instance}/companies"
    print(url)
    params = {"pageIndex": params.page_index, "pageSize": params.page_size}
    try:
        response = s.get(url, params=params, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()

@mcp.tool()
def get_time_groups(
    company_number: Optional[int] = Field(None, description="Company number."),
    time_group_code: Optional[str] = Field(None, description="Time group code."),
    page_index: Optional[int] = Field(0, description="Page index for search. Begins at 0."),
    page_size: Optional[int] = Field(20, description="Number of entries per page.")
) -> dict:
    """Gets a list of time groups. Optional to specify search parameters."""
    url = f"{consts.API_ENDPOINT}/api/timegroups"
    parameters = {"pageIndex": page_index, "pageSize": page_size}
    if company_number is not None:
        parameters["companynumber"] = company_number
    if time_group_code is not None:
        parameters["code"] = time_group_code
    
    try:
        response = s.get(url, parameters=parameters, timeout=consts.API_TIMEOUT)
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
        response = s.get(url, timeout=consts.API_TIMEOUT)
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
        response = s.get(url, timeout=consts.API_TIMEOUT)
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
        response = s.get(url, params=params, timeout=consts.API_TIMEOUT)
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
        response = s.post(
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
        response = s.put(
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
        response = s.post(
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
        response = s.post(
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
        response = s.get(
        url, 
        params=params, 
        timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_unions(
    filters: Union = Field(..., description="Union details for filtering the unions list. All fields are optional and used for filtering the results.")
)-> dict:
    """
    Filter unions by specified criteria.

    Returns:
        A JSON dict containing the list of unions.
    """
    url = f"{consts.API_ENDPOINT}/api/unions"
    params = filters.model_dump(by_alias=True, exclude_none=True)
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_union_by_id(
    union_id: UUID = Field(..., description="UUID of the union.")
) -> dict:
    """
    Get a union by id.

    Returns:
        A JSON dict containing the union details.
    """
    url = f"{consts.API_ENDPOINT}/api/unions/{union_id}"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_user_by_id(
    user_id: UUID = Field(..., description="UUID of the user.")
    )-> dict:
    """
    Gets user information by ID

    Returns:
        User data as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/users/{user_id}"
    try:
        response = s.get(url,
        timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_users(
    filters: GetUsers = Field(..., description="User details for filtering the users list. All fields are optional")
    )->dict:
    """
    Filter users of instance by specified criteria. If no instance is provided, defaults to the default-domain instance.

    Returns:
        A JSON dict containing the list of users.
    """

    url = f"{consts.API_ENDPOINT}/api/users"
    try:
        response = s.get(
            url,
            params=filters.model_dump(by_alias=True, exclude_none=True),
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_users_by_instance(
    filters: GetUsersByInstance = Field(..., description="User details for filtering the users list. All fields are optional")
    )->dict:
    """
    Filter users of a given instance by specified criteria. If no instance is provided, defaults to the default-domain instance.

    Returns:
        A JSON dict containing the list of users.
    """
    url = f"{consts.API_ENDPOINT}/api/instance/{filters.instance}/users"
    params = filters.model_dump(by_alias=True, exclude_none=True, exclude={"instance"})
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_vehicle_type(
    filters: GetVehicleType = Field(..., description="Vehicle type details for filtering the vehicle types list. All fields are optional")
    )->dict:
    """"
    Filter vehicle types by specified criteria.

    Returns:
        A paginated JSON response containing a list of matching vehicle type objects.
    """
    url = f"{consts.API_ENDPOINT}/api/vehicletypes"
    params = filters.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()


#@mcp.tool()
def create_vehicle_type(
    vehicle_type: VehicleTypeRequestModel = Field(..., description="Vehicle type details for creating a new vehicle type. All fields are optional.")
    )->dict:
    """
    Create a new vehicle type with the specified details.

    Returns:
        The created vehicle type object as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/vehicletypes"
    payload = vehicle_type.model_dump(by_alias=True, exclude_none=True)
    try:
        response = s.post(
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
def get_vehicle_type_by_company_id(
    filters: GetVehicleTypeByCompanyId = Field(..., description="Vehicle type details for filtering the vehicle types list. CompanyId is required. All fields are optional")
    )->dict:
    """
    Filter vehicle types by specified criteria for a given company. CompanyId is required.

    Returns:
        A paginated JSON response containing a list of matching vehicle type objects.
    """
    url = f"{consts.API_ENDPOINT}/api/company/{filters.company_id}/vehicletypes"
    params = filters.model_dump(by_alias=True, exclude_none=True, exclude={"company_id"})

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_vehicle_type_by_id(
    id: UUID = Field(..., description="UUID of the vehicle type.")
    )->dict:
    """
    Get vechicle type information by id.

    Returns:
        The vehicle type information as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/vehicletypes/{id}"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def update_vehicle_type(
    id: UUID = Field(..., description="UUID of the vehicle type."),
    vehicle_type: VehicleTypeRequestModel = Field(..., description="Updated vehicle type details. All fields are optional.")
    )->dict:
    """
    Update a vehicle type by id.

    Returns:
        The updated vehicle type information as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/vehicletypes/{id}"
    payload = vehicle_type.model_dump(by_alias=True, exclude_none=True)
    try:
        response = s.put(
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
def delete_vehicle_type(
    id: UUID = Field(..., description="UUID of the vehicle type.")
    )->dict:
    """
    Delete a vehicle type by id.

    Returns
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/vehicletypes/{id}"
    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_travel_claims_by_instance(
    filters: GetTravelClaims = Field(..., description="Travel claim details for filtering the travel claims list. All fields are optional")
    )->dict:
    """
    Filter travel claims by specified criteria for a given instance. If no instance is provided, defaults to the default-domain instance.

    Returns:
        A JSON dict containing the list of travel claims.
     """
    url = f"{consts.API_ENDPOINT}/api/travelclaim"
    params = filters.model_dump(by_alias=True, exclude_none=True)
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_travel_claim_attachment_by_id(
    id: UUID = Field(..., description="UUID of the travel claim attachment.")
    )->dict:
    """
    Get travel claim attachment file by id.
    
    Returns:
         A dict containing the filename and base64 encoded file content.
    """
    url = f"{consts.API_ENDPOINT}/api/travelclaim/attachment/{id}"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    
    content_disposition = response.headers.get("Content-Disposition", "")
    filename = content_disposition.split("filename=")[-1].strip('"') if "filename=" in content_disposition else str(id)

    return {
        "filename": filename,
        "content_type": response.headers.get("Content-Type", "application/octet-stream"),
        "content_base64": base64.b64encode(response.content).decode("utf-8")
    }

@mcp.tool()
def get_travel_claims_by_company_id(
    company_id: UUID = Field(..., description="UUID of the company."),
    )->dict:
    """
    Get travel claims by company ID.

    Returns:
        A JSON dict containing the list of travel claims for the specified company.
    """

    url = f"{consts.API_ENDPOINT}/api/companies/{company_id}/publictravelclaimsauditlevels"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_qualification_by_id(
    id: UUID = Field(..., description="UUID of the qualification.")
    )->dict:
    """
    Get qualification information by id.

    Returns:
        The qualification information as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/qualifications/{id}"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_qualifications_by_instance(
    instance: Optional[str] = Field(INSTANCE, description="Domain name. If not provided, defaults to the default-domain instance."),
    company_id: Optional[UUID] = Field(None, description="UUID of the company."),
    company_number: Optional[int] = Field(None, description="Company number."),
    page_index: Optional[int] = Field(0, description="Page index for search. Begins at 0."),
    page_size: Optional[int] = Field(20, description="Number of entries per page.")
    )->dict:

    """
    Get qualifications, optionally filtered by instance or company. If no instance is provided, defaults to the default-domain instance.
    Pagination parameters are supported to control result format.

    Returns:
        A JSON dict containing the list of qualifications.
    """
    url = f"{consts.API_ENDPOINT}/api/instance/{instance}/qualifications"
    params = {"pageIndex": page_index, "pageSize": page_size, "instance": instance}
    if company_id is not None:
        params["companyId"] = company_id
    if company_number is not None:
        params["companyNumber"] = company_number

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_qualifications_by_company_id(
    instance: Optional[str] = Field(INSTANCE, description="Domain name. If not provided, defaults to the default-domain instance."),
    company_id: UUID = Field(..., description="UUID of the company."),
    company_number: Optional[int] = Field(None, description="Company number."),
    page_index: Optional[int] = Field(0, description="Page index for search. Begins at 0."),
    page_size: Optional[int] = Field(20, description="Number of entries per page."),
    )->dict:
    """
    Get qualifications for a given company. Company ID is required. If no instance is provided, defaults to the default-domain instance.

    Returns:
        A JSON dict containing the list of qualifications for the specified company.
    """
    url = f"{consts.API_ENDPOINT}/api/instance/{instance}/company/{company_id}/qualifications"
    params = {"instance": instance, "companyId": company_id, "pageIndex": page_index, "pageSize": page_size}
    if company_number is not None:
        params["companyNumber"] = company_number
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_all_qualifications(
    instance: Optional[str] = Field(INSTANCE, description="Domain name. If not provided, defaults to the default-domain instance."),
    company_id: Optional[UUID] = Field(None, description="UUID of the company."),
    comopany_number: Optional[int] = Field(None, description="Company number."),
    page_index: Optional[int] = Field(0, description="Page index for search. Begins at 0."),
    page_size: Optional[int] = Field(20, description="Number of entries per page.")
    )->dict:
    """
    Gets qualifications for all isntances if no instance is provided, filtered by company_id or company_number.

    Returns:
        A JSON dict containing the list of qualifications.
    """
    url = f"{consts.API_ENDPOINT}/api/qualifications"
    params = {"pageIndex": page_index, "pageSize": page_size}
    if instance is not None:
        params["instance"] = instance
    if company_id is not None:
        params["companyId"] = company_id
    if comopany_number is not None:
        params["companyNumber"] = comopany_number
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

if __name__ == "__main__":
    mcp.run()


