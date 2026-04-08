from mcp.server.fastmcp import FastMCP
import requests
from pydantic import Field
from uuid import UUID
from datetime import date, datetime
from typing import Optional
from models import *
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
def list_instances():
    url = f"{consts.API_ENDPOINT}/instances"

    try:
        response = s.get(url, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

#Works
def get_absence_applications_by_company_id(
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company."),
    page_index: Optional[int] = Field(0, alias="pageIndex", description="Page index dafault value 0."),
    page_size: Optional[int] = Field(20, alias="pageSize", description="Page size dafault value 20.")
) -> dict:
    """
    Gets absence applications for a given company.

    Returns:
        A JSON dict containing the list of absence applications.
    """
    url = f"{consts.API_ENDPOINT}/companies/{company_id}/absenceapplications"
    params = {"pageIndex": page_index, "pageSize": page_size}
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
def get_absence_application_by_parameters(
    employmentnumber: Optional[str] = Field(None,description="Employment number."),
    instance: Optional[str] = Field(None, description="Domain name."),
    companynumber: Optional[int] = Field(None, description="Company number."),
    absence_type_id: Optional[UUID] = Field(None, alias="absenceTypeId", description="UUID of the absence type."),
    absence_type_name: Optional[str] = Field(None, alias="absenceTypeName", description="Name of the absence type."),
    page_index: Optional[int] = Field(0, alias="pageIndex", description="Page index dafault value 0."),
    page_size: Optional[int] = Field(20, alias="pageSize", description="Page size dafault value 20.")
)-> dict:
    """
    Gets absence applications filtered by the provided parameters. All parameters are optional.
    """
    url = f"{consts.API_ENDPOINT}/absenceapplications"
    params = {"pageIndex": page_index, "pageSize": page_size}
    if employmentnumber is not None:
        params["employmentnumber"] = employmentnumber
    if instance is not None:
        params["instance"] = instance
    if companynumber is not None:
        params["companynumber"] = companynumber
    if absence_type_id is not None:
        params["absenceTypeId"] = absence_type_id
    if absence_type_name is not None:
        params["absenceTypeName"] = absence_type_name
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
def create_absence_application(
    apply_approval: Optional[bool] = Field(False, description="Decides whether the absence application has automatic approval to the highest level. Default value false."),
    is_part_time_absence: Optional[bool] = Field(False, description="Decides whether the absence application is part time absence. Default false."),
    application: ImportAbsenceApplicationModelAPIBase = Field(..., description="Full absence application object. absenceTypeId, companyID, employmentNumber, fromDate,and Id are requiered. All other fields are optional ")
    )-> dict:
    """
    Creates an absence application. The request body must include absenceTypeId, companyID, employmentNumber, fromDate, and Id at minimum.

    Returns:
        API response as a JSON dict.
     """
    url = f"{consts.API_ENDPOINT}/absenceapplications"
    params = {"applyApproval": apply_approval, "isPartTimeAbsence": is_part_time_absence}
    payload = application.model_dump(by_alias=True, exclude_none=True)
    try:
        response = s.post(
            url,
            params=params,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()
@mcp.tool()

def get_absence_application_by_id(
    id: UUID = Field(..., description="UUID of the absence application.")
    )-> dict:
    """
    Gets an absence application by id.

    Returns:
        A JSON dict containing the absence application details.
    """
    url = f"{consts.API_ENDPOINT}/absenceapplications/{id}"
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
def delete_absence_application_by_id(
    id: UUID = Field(..., description="UUID of the absence application.")
    )-> dict:
    """
    Deletes an absence application by id.

    Returns:
        API response as a JSON dict.
     """
    url = f"{consts.API_ENDPOINT}/absenceapplications/{id}"
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
def update_absence_application(
    id: UUID = Field(description="Absence application id"),
    apply_approval: Optional[bool] = Field(False, description="Decides whether the absence application has automatic approval to the highest level. Default value false."),
    is_part_time_absence: Optional[bool] = Field(False, description="Decides whether the absence application is part time absence. Default false."),
    application: ImportAbsenceApplicationModelAPIBase = Field(description="Updated parameters for the application. absenceTypeId, companyId, employmentNumber, fromDate and Id are required")
)->dict:
    """
    Updates a specfied absence applicaiton

    Returns:
        API response as JSON dict
    """
    url = f"{consts.API_ENDPOINT}/absenceapplications/{id}"
    params = {}
    if apply_approval is not None:
        params["applyApproval"] = apply_approval
    if is_part_time_absence is not None:
        params["isPartTimeAbsence"] = is_part_time_absence
    payload = application.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.put(
            url,
            params=params,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_absence_types_by_company_id(
    comapany_id: UUID = Field(..., description="UUID of the company."),
    page_index: Optional[int] = Field(0, alias="pageIndex", description="Page index dafault value 0."),
    page_size: Optional[int] = Field(20, alias="pageSize", description="Page size dafault value 20"),
    absence_type_name: Optional[str] = Field(None, alias="absenceTypeName", description="Name of the absence type."),
)-> dict:
    """
    Gets absence types for a given company.
    
    Returns:
    A JSON dict containing the list of absence types.
    """
    url = f"{consts.API_ENDPOINT}/companies/{comapany_id}/absencetypes"
    params = {"pageIndex": page_index, "pageSize": page_size}
    if absence_type_name is not None:
        params["absenceTypeName"] = absence_type_name
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
def get_absence_type_by_parameters(
    page_index: Optional[int] = Field(0, alias="pageIndex", description="Page index dafault value 0."),
    page_size: Optional[int] = Field(20, alias="pageSize", description="Page size dafault value 20"),
    absence_type_name: Optional[str] = Field(None, alias="absenceTypeName", description="Name of the absence type."),
)-> dict:
    url = f"{consts.API_ENDPOINT}/absencetypes"
    params = {"pageIndex": page_index, "pageSize": page_size}
    if absence_type_name is not None:
        params["absenceTypeName"] = absence_type_name
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
def get_absence_type_by_id(
    id: UUID = Field(..., description="UUID of the absence type.")
    )-> dict:
    """
    Gets an absence type by id.

    Returns:
        A JSON dict containing the absence type details.
     """
    url = f"{consts.API_ENDPOINT}/absencetypes/{id}"
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
def create_new_accounts(
    account_distribution_id: UUID = Field(..., description="The id of the account distribution that the accounts is created in."),
    account_model: AccountModel = Field(description="All relevant information surrounding the account. Account name and code are requiered")    
)->dict:
    """
    Creates new accounts

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accountdistributions/{account_distribution_id}/accounts"
    payload = account_model.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_accounts_by_account_distribution_id(
    account_distribution_id: UUID = Field(..., alias="accountDistributionId",description="Account distribution id to select by"),
    filters: GetAccountByAccountDistributionId = Field(description="filter parameters, all parameters optional")
)->dict:
    """
    Get accounts by distribution id

    Returns: 
        API response as a a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accountdistributions/{account_distribution_id}/accounts"
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
def update_account_by_id(
    id: UUID = Field(..., description="Account id"),
    query: AccountModel = Field(description="query parameters, code and name are requiered")
)->dict:
    """
    Update account by id

    Response: 
        API response as JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accounts/{id}"
    payload = query.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_account_by_id(
    id: UUID = Field(..., description="Account id"),
    page_params: PageModel = Field(description="Page parameters")
)->dict:
    url = f"{consts.API_ENDPOINT}/accounts/{id}"
    params = page_params.model_dump(by_alias=True, exclude_none=True)
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
def delete_account_by_id(
    id: UUID = Field(..., description="Account id"),
)->dict:
    url = f"{consts.API_ENDPOINT}/accounts/{id}"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

#This GET operation requires a body payload and cannot be tested in swagger. 
# The body should be a JSON/XML object of type GetReportedHoursModel.
@mcp.tool()
def get_reported_hours(
    query: GetReportedHoursModel = Field(description="full query object all parameters are optional")
)->dict:
    """
    Gets reported hours

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accounts/GetReportedHours"
    payload = query.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.get(
            url,
            json = payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_account_budget_by_account_id(
    account_id: UUID = Field(...,description="Account id. Get account budget from the given account."),
    filters: GetAccountBudgetByAccountId = Field(description="Filers to filter the budgets within the upon")
)->dict:
    """
    Get budgets within a given account.

    Returns: 
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accounts/{account_id}/accountbudgets"
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
def create_account_budget_for_account_id(
    account_id: UUID = Field(alias="accountid",description="Account id. The account that the account budget is posted to."),
    query: AccountBudgetModel = Field(description="Id is optional all other parameters requierd")
    )->dict:
    """
    Creates new account budget instances for given account by the account id

    Response:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/account/{account_id}/accountbudgets"
    payload = query.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def update_account_budget_by_id(
    id: UUID = Field(...,description="UUID of the account budget"),
    query: AccountBudgetModel = Field(description="Id is optional all other parameters requierd")
    )->dict:
    url = f"{consts.API_ENDPOINT}/accountbudgets/{id}"
    payload = query.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def create_account_combination(
    query: AccountCombinationModel = Field(description="Full query object, id is optional all other parameters required")
)->dict:
    """
    Creates an account combination

    Response:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accountcombinations"
    payload = query.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def update_account_combination_by_id(
    id: UUID = Field(...,description="UUID of the account combination"),
    query: AccountCombinationModel = Field(description="Full query object, id is optional all other parameters required")
    )->dict:
    """
    Updates an account combination

    Response:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accountcombinations/{id}"
    payload = query.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

@mcp.tool()
def get_account_combination_by_id(
    id: UUID = Field(...,description="UUID of the account combination")
    )->dict:
    """
    Get an account combination by id

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accountcombinations/{id}"

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
def delete_account_combination_by_id(
    id: UUID = Field(...,description="UUID of the account combination")
    )->dict:
    """
    Delete an account combination by id

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accountcombinations/{id}"

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
def get_account_combination_by_account_id(
    account_id: UUID = Field(...,description="UUID of the acccount"),
    page_params: PageModel = Field(description="Page parameters")
    )->dict:
    """
    Get account combinations for an account by accont id

    Reponse:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accounts/{account_id}/accountcombinations"
    params = page_params.model_dump(by_alias=True, exclude_none=True)

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
def get_account_combination_by_account_distribution_id_and_account_code(
    account_distribution_id: UUID = Field(...,alias="accountDistributionId",description="UUID of the account distribution"),
    account_code: str = Field(...,alias="accountCode",description="Accound code"),
    page_params: PageModel = Field(description="Page parameters")
)->dict:
    """
    Get account combinations by accountdistribution and account code.

    Returns: 
        API response as a JSON Dict
    """
    url = f"{consts.API_ENDPOINT}/accountdistributions/{account_distribution_id}/accounts/{account_code}/accountcombinations"
    params = page_params.model_dump(by_alias=True, exclude_none=True)

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
def get_account_distribution_by_company_number(
    query: GetAccountDistribution = Field(...,description="Full query object, company requiered, instance will default to default instance if not provided ")
    )->dict:
    """
    Get account distribution for a given company number in a given instance, if no instance is provided will use default instance.

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accountdistributions"
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

@mcp.tool()
def get_account_distribution_by_company_id(
    company: UUID = Field(...,description="UUID of the company"),
    page_params: PageModel = Field(description="Page parameters")
    )->dict:
    """
    Get account distribution for a company id.

    Response:
        API response as JSON dict
    """
    url = f"{consts.API_ENDPOINT}/companies{company}/accountdistributions"
    params = page_params.model_dump(by_alias=True, exclude_none=True)

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
def get_salary_by_id(
    salary_id: UUID = Field(..., description="UUID of the salary."),
) -> dict:
    """
    Gets a salary by id.

    Returns:
        Salary data as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/salaries/{salary_id}"

    try:
        response = s.get(url, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()

#Works
#@mcp.tool()
def update_salary_by_id(
    salary_id: UUID = Field(..., description="UUID of the salary."),
    salary_data: Salary = Salary()
) -> dict:
    """
    Updates a salary by id.

    Returns:
        Updated salary data as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/salaries/{salary_id}"
    try:
        response = s.put(
            url,
            json=salary_data.model_dump(by_alias=True, exclude_none=True),
            headers={"Content-Type": "application/json"},
            timeout=consts.API_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()

#Works
@mcp.tool()
def delete_salary(
    salary_id: UUID = Field(..., description="UUID of the salary"),
) -> dict:
    """
    Deletes a salary by id.

    Returns:
        Status code. (200 = OK)
    """
    url = f"{consts.API_ENDPOINT}/salaries/{salary_id}"

    try:
        response = s.delete(
            url, 
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.status_code

#Works?
@mcp.tool()
def get_salaries_by_instance(
    query: GetSalaries = GetSalaries()
    ) -> dict:
    """
     Get salaries for a given instance. If no instance is provided, defaults to the default-domain instance.

    Returns:
        A JSON dict containing the list of salaries.
    """
    url = f"{consts.API_ENDPOINT}/instance/{query.instance}/salaries"

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
#print(get_salaries_by_instance(GetSalaries()))

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
    url = f"{consts.API_ENDPOINT}/instance/{query.instance}/company/{query.company_id}/salaries"

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
#print(get_salaries_by_company(GetSalariesByCompany(companyId="b4253a61-f229-4ca9-9831-ad931d9a75a6")))
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
    
    url = f"{consts.API_ENDPOINT}/instance/{query.instance}/company/{query.company_id}/employee/{query.employee_id}/salaries"

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
    query: GetSalariesByEmployee = Field(..., description="Full query object. employee_id is required. All other fields are optional")
    ) -> dict:
    """
     Get salaries for an employee.

     Returns: 
        A JSON dict containing the list of salaries.
    """
    url = f"{consts.API_ENDPOINT}/employee/{query.employee_id}/salaries"

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
#print(get_salaries_by_employee(GetSalariesByEmployee(employee_id="640ca4b1-bf59-4740-9fc6-b1c6008861a0")))


#@mcp.tool()
def update_salaries_by_employee(
    query: UpdateOrCreateSalaries = Field(..., description="Full query object. Employee_id, and company_id are required. All other fields are optional")
    ) -> dict:
    """
     Update salaries for an employee of a given company for a given isntance-id. If no instanceid is provided, uses default instance-id. 

     Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employees/{query.employee_id}/salaries"

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
    query: GetAllSalaries = GetAllSalaries()
    ) -> dict:
    """
     Get salaries.
     """
    url = f"{consts.API_ENDPOINT}/salaries"

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
#print(get_all_salaries())

#@mcp.tool()
def create_salary(
    query: UpdateOrCreateSalaries = Field(..., description="Full query object. Employee_id, and company_id are required. All other fields are optional")
    ) -> dict:
    """
     Create a salary for an employee of a given company for a given instance-id. If no instance id is provided, uses default instance-id. 

     Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/salaries"

    payload = query.model_dump(mode="json", by_alias=True, exclude_none=True)

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

#print(create_salary(UpdateOrCreateSalaries(company_id=UUID("b4253a61-f229-4ca9-9831-ad931d9a75a6"), employee_id=UUID("f83fe21a-a90a-4ce8-8a13-b1c60089eca5") ,salary_type=0, full_time_salary=1200, comment="Bombaclat", is_historical_salary=True, from_date=datetime(2026, 4, 3, 0, 0, 0, 0))))

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
    url = f"{consts.API_ENDPOINT}/employees/{employee_id}/timereport"

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
    url = f"{consts.API_ENDPOINT}/employees/{employee_id}"

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
            url=f"{consts.API_ENDPOINT}/employees/{employee_id}/timereports/{date.isoformat()}",
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
    page_index: Optional[int] = Field(0, alias="pageIndex", description="Page index dafault value 0."),
    page_size: Optional[int] = Field(20, alias="pageSize", description="Page size dafault value 20.")
) -> dict:
    """
    Gets a list of employment periods by employee id.

    Returns:
        The employment periods from and to dates, id of resignation cause and type of employment.
    """
    url = f"{consts.API_ENDPOINT}/employees/{employee_id}/employmentperiods"
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

#Works
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
    page_index: Optional[int] = Field(0, alias="pageIndex", description="Page index dafault value 0."),
    page_size: Optional[int] = Field(20, alias="pageSize", description="Page size dafault value 20.")
) -> dict:
    """Gets a list of time groups. Optional to specify search parameters."""
    url = f"{consts.API_ENDPOINT}/timegroups"
    params = {"pageIndex": page_index, "pageSize": page_size}
    if company_number is not None:
        params["companynumber"] = company_number
    if time_group_code is not None:
        params["code"] = time_group_code

    try:
        response = s.get(url, paramsrs=params, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    return response.json()

#Works
@mcp.tool()
def get_company(
    company_id: UUID = Field(..., description="UUID of the company.")
    ) -> dict:
    """
    Gets company information by id.

    Returns:
        The detailed company information as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/companies/{company_id}"

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
    url = f"{consts.API_ENDPOINT}/projects/{project_id}"

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
    url = f"{consts.API_ENDPOINT}/employees/{employee_id}/scheduledays"
 
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
    url = f"{consts.API_ENDPOINT}/employees/{employee_id}/timerow/{row_date.isoformat()}"
 
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
    url = f"{consts.API_ENDPOINT}/projects/{project_id}"
 
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

    url = f"{consts.API_ENDPOINT}/stamping/{userId}/inOut"

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
    url = f"{consts.API_ENDPOINT}/employees/{employeeId}/inOut"

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
    
    url = f"{consts.API_ENDPOINT}/stamping/{user_id}/timeRows"

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

#Works
@mcp.tool()
def get_unions(
    filters: Union = Field(..., description="Union details for filtering the unions list. All fields are optional and used for filtering the results.")
)-> dict:
    """
    Filter unions by specified criteria.

    Returns:
        A JSON dict containing the list of unions.
    """
    url = f"{consts.API_ENDPOINT}/unions"
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
    url = f"{consts.API_ENDPOINT}/unions/{union_id}"
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
    url = f"{consts.API_ENDPOINT}/users/{user_id}"
    try:
        response = s.get(url,
        timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

#Works
@mcp.tool()
def get_users(
    filters: GetUsers = GetUsers()
    )->dict:
    """
    Filter users of instance by specified criteria.
    Returns:
        A JSON dict containing the list of users.
    """

    url = f"{consts.API_ENDPOINT}/users"
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
    url = f"{consts.API_ENDPOINT}/instance/{filters.instance}/users"
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

#Works
@mcp.tool()
def get_vehicle_type(
    filters: GetVehicleType = GetVehicleType()
    )->dict:
    """"
    Filter vehicle types by specified criteria.

    Returns:
        A paginated JSON response containing a list of matching vehicle type objects.
    """
    url = f"{consts.API_ENDPOINT}/vehicletypes"
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
    url = f"{consts.API_ENDPOINT}/vehicletypes"
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
    url = f"{consts.API_ENDPOINT}/company/{filters.company_id}/vehicletypes"
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
    url = f"{consts.API_ENDPOINT}/vehicletypes/{id}"
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
    url = f"{consts.API_ENDPOINT}/vehicletypes/{id}"
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
    url = f"{consts.API_ENDPOINT}/vehicletypes/{id}"
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
def get_travel_claims(
    filters: GetTravelClaims = Field(..., description="Travel claim details for filtering the travel claims list. All fields are optional")
    )->dict:
    """
    Filter travel claims by specified criteria for a given instance.

    Returns:
        A JSON dict containing the list of travel claims.
     """
    url = f"{consts.API_ENDPOINT}/travelclaim"
    params = filters.model_dump(by_alias=True, exclude_none=True, mode="json")
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
    url = f"{consts.API_ENDPOINT}/travelclaim/attachment/{id}"
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

    url = f"{consts.API_ENDPOINT}/companies/{company_id}/publictravelclaimauditlevels"
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
    url = f"{consts.API_ENDPOINT}/qualifications/{id}"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()

#Works (not)
@mcp.tool()
def get_qualifications_by_instance(
    instance: Optional[str] = Field(INSTANCE, description="Domain name. If not provided, defaults to the default-domain instance."),
    company_id: Optional[UUID] = Field(None, description="UUID of the company."),
    company_number: Optional[int] = Field(None, description="Company number."),
    page_index: Optional[int] = Field(0, alias="pageIndex", description="Page index dafault value 0."),
    page_size: Optional[int] = Field(20, alias="pageSize", description="Page size dafault value 20.")
    )->dict:

    """
    Get qualifications, optionally filtered by instance or company. If no instance is provided, defaults to the default-domain instance.
    Pagination parameters are supported to control result format.

    Returns:
        A JSON dict containing the list of qualifications.
    """
    url = f"{consts.API_ENDPOINT}/instance/{instance}/qualifications"
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
    page_index: Optional[int] = Field(0, alias="pageIndex", description="Page index dafault value 0."),
    page_size: Optional[int] = Field(20, alias="pageSize", description="Page size dafault value 20."),
    )->dict:
    """
    Get qualifications for a given company. Company ID is required. If no instance is provided, defaults to the default-domain instance.

    Returns:
        A JSON dict containing the list of qualifications for the specified company.
    """
    url = f"{consts.API_ENDPOINT}/instance/{instance}/companies/{company_id}/qualifications"
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

#Works (not)
@mcp.tool()
def get_all_qualifications(
    instance: Optional[str] = Field(None, description="Domain name."),
    company_id: Optional[UUID] = Field(None, description="UUID of the company."),
    comopany_number: Optional[int] = Field(None, description="Company number."),
    page_index: Optional[int] = Field(0, alias="pageIndex", description="Page index dafault value 0."),
    page_size: Optional[int] = Field(20, alias="pageSize", description="Page size dafault value 20.")
    )->dict:
    """
    Gets qualifications for all instances. If no instance is provided, filtered by company_id or company_number.

    Returns:
        A JSON dict containing the list of qualifications.
    """
    url = f"{consts.API_ENDPOINT}/qualifications"
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
#print(get_all_qualifications())


if __name__ == "__main__":
    mcp.run()