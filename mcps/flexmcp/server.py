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

def list_instances():
    url = f"{consts.API_ENDPOINT}/instances"

    try:
        response = s.get(url, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"



@mcp.tool()
def get_all_employees() -> dict:
    """
    Gets all employees

    Returns:
        Employee data as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employees"

    try:
        response = s.get(url, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    return response.json()


#Works
@mcp.tool()
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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_absence_application_by_parameters(
    params: GetAbsenceApplicationByParameters = GetAbsenceApplicationByParameters()
)-> dict:
    """
    Gets absence applications filtered by the provided parameters. All parameters are optional.

    Returns:
        API response as JSON ditct
    """
    url = f"{consts.API_ENDPOINT}/absenceapplications"
    params = params.model_dump(by_alias=True, exclude_none=True)
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def create_absence_application(
    params: CreateAbsenceApplicationQuery = CreateAbsenceApplicationQuery(),
    application: ImportAbsenceApplicationModelAPIBase = Field(..., description="Full absence application object. absenceTypeId, companyID, employmentNumber, fromDate,and Id are requiered. All other fields are optional ")
    )-> dict:
    """
    Creates an absence application. The request body must include absenceTypeId, companyID, employmentNumber, fromDate, and Id at minimum.

    Returns:
        API response as a JSON dict.
     """
    url = f"{consts.API_ENDPOINT}/absenceapplications"
    params = params.model_dump(by_alias=True, exclude_none=True)
    payload = application.model_dump(by_alias=True, exclude_none=True, mode="json")
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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    return response.status_code

@mcp.tool()
def update_absence_application(
    id: UUID = Field(..., description="Absence application id, required."),
    query: UpdateAbsenceApplicationQuery = UpdateAbsenceApplicationQuery(),
    application: ImportAbsenceApplicationModelAPIBase = Field(..., description="Updated parameters for the application. absenceTypeId, companyId, employmentNumber, fromDate and Id are required")
)->dict:
    """
    Updates a specfied absence applicaiton

    Returns:
        API response as JSON dict
    """
    url = f"{consts.API_ENDPOINT}/absenceapplications/{id}"
    params = query.model_dump(by_alias=True, exclude_none=True)
    payload = application.model_dump(by_alias=True, exclude_none=True, mode="json")
    try:
        response = s.put(
            url,
            params=params,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_absence_types_by_company_id(
    comapany_id: UUID = Field(..., description="UUID of the company."),
    query: GetAbsenceTypes = GetAbsenceTypes()
)-> dict:
    """
    Gets absence types for a given company.
    
    Returns:
    A JSON dict containing the list of absence types.
    """
    url = f"{consts.API_ENDPOINT}/companies/{comapany_id}/absencetypes"
    params = query.model_dump(by_alias=True, exclude_none=True)
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_absence_types(
    query: GetAbsenceTypes = GetAbsenceTypes()
)-> dict:
    url = f"{consts.API_ENDPOINT}/absencetypes"
    params = query.model_dump(by_alias=True, exclude_none=True)
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
    url = f"{consts.API_ENDPOINT}/accountdistributions/{str(account_distribution_id)}/accounts"
    payload = account_model.model_dump(by_alias=True, exclude_none=True, mode="json")
    print(payload)
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_accounts_by_account_distribution_id(
    account_distribution_id: UUID = Field(..., alias="accountDistributionId",description="Account distribution id to select by"),
    filters: GetAccountByAccountDistributionId = GetAccountByAccountDistributionId()
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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_account_by_id(
    id: UUID = Field(..., description="Account id"),
    query: AccountModel = Field(..., description="query parameters, code and name are requiered")
)->dict:
    """
    Update account by id

    Returns: 
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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_account_by_id(
    id: UUID = Field(..., description="Account id"),
    page_params: PageModel = PageModel()
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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def create_account_budget_for_account_id(
    account_id: UUID = Field(..., alias="accountid",description="Account id. The account that the account budget is posted to."),
    query: AccountBudgetModel = Field(..., description="Id is optional, all other parameters requiered")
    )->dict:
    """
    Creates new account budget instances for given account by the account id

    Retruns:
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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def create_account_combination(
    query: AccountCombinationModel = Field(..., description="Full query object, id is optional all other parameters required")
)->dict:
    """
    Creates an account combination

    Returns:
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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_account_combination_by_id(
    id: UUID = Field(...,description="UUID of the account combination"),
    query: AccountCombinationModel = Field(..., description="Full query object, id is optional all other parameters required")
    )->dict:
    """
    Updates an account combination

    Returns:
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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_account_combination_by_account_id(
    account_id: UUID = Field(...,description="UUID of the acccount"),
    page_params: PageModel = PageModel()
    )->dict:
    """
    Get account combinations for an account by accont id

    Returns:
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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_account_combination_by_account_distribution_id_and_account_code(
    account_distribution_id: UUID = Field(...,alias="accountDistributionId",description="UUID of the account distribution"),
    account_code: str = Field(...,alias="accountCode",description="Accound code"),
    page_params: PageModel = PageModel()
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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_account_distribution_by_company_id(
    company_id: UUID = Field(..., description="UUID of the company"),
    page_params: PageModel = PageModel()
    )->dict:
    """
    Get account distribution for a company id.

    Returns:
        API response as JSON dict
    """
    url = f"{consts.API_ENDPOINT}/companies/{company_id}/accountdistributions"
    params = page_params.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_account_part_approval_permissions_by_id(
    id: UUID = Field(...,description="Account part approval permission id.")
    )->dict:
    """
    Get account part approval permission by id

    Returns:
        API response as JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accountdistributionpartapprovalpermissions/{id}"
    
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_company_account_part_aproval_permission_by_id(
    id: UUID = Field(...,description="Company account part approval id."),
    query: AccountDistributionPartApprovalPermissionModel = Field(...,description="Full query object, all parameters are requiered")
    )->dict:
    """
    Update company account part apporval permission for a given id.

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accountdistributionpartapprovalpermissions/{id}"
    payload = query.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def delete_compamny_account_approval_permission_by_id(
    id: UUID = Field(...,description="The user account part aproval permission id"),
    )->dict:
    """
    Delete company part approval permission for a given id

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accountdistributionpartapprovalpermissions/{id}"

    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_company_account_approval_permissions(
    filters: Optional[GetCompanyAccountApprovalPermississons] = GetCompanyAccountApprovalPermississons()
    )->dict:
    """
    Get company account approval permissions accordning to filer parameters.

    Retruns:
        API response as JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accountdistributionpartapprovalpermissions"
    params = filters.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def create_company_account_part_approval_permissios_by_user_id(
    user_id: UUID = Field(..., alias="userId", description="UUID of the user"),
    query: AccountDistributionPartApprovalPermissionModel = Field(..., description="Query object, all parameters requiered")
    )->dict:
    """
    Creates new company account part approval permissions for a user

    Returns:
        API response as JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accountdistributionpartapprovalpermissions"
    payload = query.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.post(
            url,
            josn=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_accumulators(
    filters: Optional[GetAccumulators] = GetAccumulators
    )->dict:
    """
    Get accumulators based on fitler parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accumulators"
    params = filters.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_accumulator_by_id(
    id: UUID = Field(...,description="UUID of the accumulator")
    )->dict:
    """
    Get accumulator by id

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accumulators/{id}"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_allowance_rule_set(
    filters: Optional[GetAllowanceRuleSet] = GetAllowanceRuleSet()
    )->dict:
    """
    Get a paged collection of allowance rule sets

    Returns:
        API response as JSON dict
    """
    url = f"{consts.API_ENDPOINT}/allowancerulesets"
    params = filters.model_dump(by_alias=True, exclude_none=True)
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_audited_time_reports_by_company(
    company_id: UUID = Field(...,alias="companyId",description="UUID of the company"),
    filters: GetAuditedTimeReportsByCompany = Field(...,description="Fiter parameters all fields are optional")
    )->dict:
    """
    Get audited time reports by comapny id

    Returns:
        API reponse as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/allowancerulesets"
    params = filters.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_background_tasks_by_id(
    id: UUID = Field(...,description="UUID of the backgroundtask")
    )->dict:
    url = f"{consts.API_ENDPOINT}/backroundtasks/{id}"
    
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_background_task(
    filters: GetBackGroundTasks = Field(description="Filter parameters all fields are optional")
    )->dict:
    """
    Get background tasks

    Retruns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/backroundtasks"
    params = filters.model_dump(by_alias=True, exclude_none=True)
    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def begin_background_task_release_accounts_to_billing(
    query: BillingReleaseSelectionModel = Field(description="Query object all fields optional")
    )->dict:
    """
    Creates a background task that releases selected accounts to billing.
    
    Returns: 
        API response as a JSON dict containing a background task object with an id 
        that can be used to track progress by calling get_background_task_by_id.
    """
    url = f"{consts.API_ENDPOINT}/backroundtasks/BEGIN_RELEASE_ACCOUNTS_TO_BILLING"
    payload = query.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def begin_background_task_rollback_release(
    query: RollbackReleaseModel = Field(description="Query object all fields optional")
    )->dict:
    """
    Creates a background task that rollbacks a billing release by release ID.

    Returns:
        API response as a JSON dict containing a background task object with an id 
        that can be used to track progress by calling get_background_task_by_id.
    """
    url = f"{consts.API_ENDPOINT}/backroundtasks/BEGIN_ROLLBACK_RELEASE"
    payload = query.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_balances(
    filters: GetBalances = Field(description="Filter object all fields are optional")
    )->dict:
    """
    Get balances by filter parameters

    Retruns: 
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/balances"
    params = filters.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_balances_by_company_id(
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company"),
    filters: Optional[GetBalancesByCompanyId] = GetBalancesByCompanyId()
) -> dict:
    """
    Get balances for a company by company id optionaly filterd by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/companies/{company_id}/balances"
    params = filters.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_balance_by_id(
    id: UUID = Field(...,description="UUID of the balance")
    )->dict:
    """
    Get a balance by id

    Returns: 
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/balances/{id}"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_balance_adjustment_by_id(
    id: UUID = Field(...,description="UUID of the balance adjustment")
    )->dict:
    """
     Get a balance adjustment by id

    Returns: 
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/balanceadjustments/{id}"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def delete_balance_adjustment_by_id(
    id: UUID = Field(...,description="UUID of the balance adjustment")
    )->dict:
    """
     delete a balance adjustment by id

    Returns: 
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/balanceadjustments/{id}"

    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_balance_adjustment_by_id(
    query: BalanceAdjustmentModel  = Field(...,description="Query object")
    )->dict:
    """
    Update a balance adjustment record by id

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/balanceadjustments/{id}"
    payload = query.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_balance_adjustment_by_employee_id(
    id: UUID = Field(...,description="UUID of the employee"),
    filter: Optional[GetBalanceAdjustmentByEmployeeOrCompany] = Field(GetBalanceAdjustmentByEmployeeOrCompany(),description="Optinal filter parameters")
    )->dict:
    """
    Get balande adjustment for an employee given by employee id

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employees/{id}/balanceadjustments"
    params = filter.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_balance_adjustment_by_company_id(
    id: UUID = Field(...,description="UUID of the company"),
    filter: Optional[GetBalanceAdjustmentByEmployeeOrCompany] = Field(GetBalanceAdjustmentByEmployeeOrCompany(),description="Optinal filter parameters")
    )->dict:
    """
    Get balande adjustment for a company given by company id

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/companies/{id}/balanceadjustments"
    params = filter.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_balance_adjustments(
    filters: Optional[GetBalanceAdjustments] = Field(GetBalanceAdjustments(),description="Filer parameters all feilds are optinal")
    )->dict:
    """
    Get balance adjustments filtered by filter parameters

    Returns:
        API response as JSON dict
    """
    url = f"{consts.API_ENDPOINT}/balanceadjustments"
    params = filter.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def create_balance_adjustment_batch_by_company(
    id: UUID = Field(...,description="UUID of the company"),
    query: List[BalanceAdjustmentModel]  = Field(...,description="Query object")
    )->dict:
    """
    Post a batch of balance adjustmets by company

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/companies/{id}/balanceadjustments/batch"
    
    balance_adjustments = [
        BalanceAdjustmentModel(**balance_adjustment) if isinstance(balance_adjustment, dict) else balance_adjustment
        for balance_adjustment in query
    ]

    payload = [balance_adjustment.model_dump(mode="json", by_alias=True, exclude_none=True) for balance_adjustment in balance_adjustments]
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_balance_report_by_balance_id_and_employee_id(
    balance_id: UUID = Field(...,alias="balanceId",description="UUID of the balance"),
    filters: GetBalanceReportByBalanceIdAndEmployeeId = Field(..., description="Parameters to filter the results by, employeeId and balanceTypeValueEnum requiered all other fields optional")
    )->dict:
    """
    Get a balance report by balance id and employee id

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/balance/{balance_id}/balancereport"
    params = filters.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_billing_releases_by_company(
    filters: GetBillingReleasesByCompany = Field(...,description="Parameters to filter the search by: company and instance are required, if no isntance is provied will use default instance.")
    )->dict:
    """"
    Gets billing releases for a company in a given isntance,if no isntance is provied will use default instance."

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/billingreleases"
    params = filters.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_billing_releases_by_id(
    id: UUID = Field(...,description="UUID of the billing release")
    )->dict:
    url = f"{consts.API_ENDPOINT}/billingreleases/{id}"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def check_status()->dict:
    """
    Check API status

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/CheckStatus"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        url = f"{consts.API_ENDPOINT}/CheckStatusWorkServer"
        response.raise_for_status()
        response = response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.status_code

@mcp.tool()
def get_child_by_id(
    id: UUID = Field(...,description="UUID of the child")
    )->dict:
    """
    Get a child by id

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/child/{id}"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_child_by_id_put(
    id: UUID = Field(...,description="UUID of the child"),
    query: ChildModel = Field(...,description="Full query object")
    )->dict:
    """
    Update a child by id (put)

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/child/{id}"
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_child_by_id_post(
    id: UUID = Field(...,description="UUID of the child"),
    query: ChildModel = Field(...,description="Full query object")
    )->dict:
    """
    Create a child by id (post)

    Returns:
        API response as a JSON dict
    """

    url = f"{consts.API_ENDPOINT}/child/{id}"
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def delete_child_by_id(
    id: UUID = Field(...,description="UUID of the child")
    )->dict:
    """
    Delete a child by id

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/child/{id}"

    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_children(   
    filters: Optional[GenericGetModel] = Field(GenericGetModel(), description="Parameters to search the children by, all feilds optinal")
    )->dict:
    url = f"{consts.API_ENDPOINT}/child"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def create_child(
    query: ChildModel = Field(...,description="Full query object")
    )->dict:
    """
    Create a new child

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/child"
    payload = query.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

#Works
@mcp.tool()
def get_company_by_id(
    company_id: UUID = Field(..., description="UUID of the company.")
    ) -> dict:
    """
    Gets company information by id.

    Returns:
        The detailed company information as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/companies/{company_id}"

    try:
        response = s.get(
            url, 
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_company_by_id_put(
    id: UUID = Field(..., description="UUID of the company."),
    query: Optional[CompanyModel] = Field(CompanyModel(),description="Full query obejct, all fields optional")
    )->dict:
    """
    Update company by id (put)

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/companies/{id}"
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.get(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_company_by_id_post(
    id: UUID = Field(..., description="UUID of the company."),
    query: Optional[CompanyModel] = CompanyModel()
    )->dict:
    """
    Update company by id (post)

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/companies/{id}"
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_companies(
    filters: Optional[GetCompanies] = GetCompanies()
    )->dict:
    """"
    Get companies optionally filtered by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/companies"
    params = filters.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def create_company(
    company_id_to_copy_from: Optional[UUID] = Field(None, alias="companyIdToCopyFrom", description="UUID of the company to copy settings from."),
    copy_settings: Optional[int] = Field(None, alias="copySettings", description="Settings determining what to copy from the given company."),
    query: CompanyPostRequestModel = Field(..., description="Company details to create.")
) -> dict:
    """
    Creates a new company.

    Returns:
        A JSON dict containing the created company object.
    """

    url = f"{consts.API_ENDPOINT}/companies"
    payload = query.model_dump(by_alias=True, exclude_none=True),
    params = {}
    if company_id_to_copy_from is not None:
        params["companyIdToCopyFrom"] = str(company_id_to_copy_from)
    if copy_settings is not None:
        params["copySettings"] = copy_settings

    try:
        response = requests.post(
            url,
            params=params,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_customer_by_id(
    id: UUID = Field(..., description="UUID of the customer."),
    )->dict:
    """
    Get a customer by Id

    Retruns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/customers/{id}"
    try:
        response = requests.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"    

mcp.tool()
def update_customer_by_id(
    id: UUID = Field(..., description="UUID of the customer."),
    query: CustomerModel = Field(...,description="Full query object")
    )->dict:
    """
    Updates a customer by customer id

    Retuerns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/customers/{id}"
    payload = query.model_dump(by_alias=True, exclude_none=True),

    try:
        response = requests.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def detlete_customer_by_id(
    id: UUID = Field(..., description="UUID of the customer."),
    )->dict:
    """
    delete a customer by Id

    Retruns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/customers/{id}"
    try:
        response = requests.delete(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

mcp.tool()
def get_customers_by_company(
    filters: GetCustomersByComopany = Field(...,description="Filter parameters to fitler the search by, company and isntance are requiered, if no isntance is provided will default to default instance")
    )->dict:
    """
    Get customers by company optinaly filtered by filter parameters

    Returns:
        API response as JSON dict
    """
    url = f"{consts.API_ENDPOINT}/customers"
    params = filters.model_dump(by_alias=True,exclude_none=True)

    try:
        response = requests.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_customers_by_account_distribution_id(
    account_distirbution_id: UUID = Field(...,description="UUID of the account distribution."),
    filters: Optional[GetCustomersByAccountDistribution] = GetCustomersByAccountDistribution()
    )->dict:
    """
    Get customers by account distribution id

    Response:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/accountdistributions/{account_distirbution_id}/customers"
    params = filters.model_dump(by_alias=True,exclude_none=True)

    try:
        response = requests.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def post_customers_by_account_distribution_id(
    account_distirbution_id: UUID = Field(..., description="UUID of the account distribution."),
    query: CustomerModel = Field(..., description="Fully query object")
    )->dict:
    """
    Posts customers by account distribution id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/accountdistributions/{account_distirbution_id}/customers"
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_from_time_schedule_by_employee_and_date(
    filters: GetTimeScheduleByEmployeeAndDate = Field(..., description="Filter parameters to fitler the search by, all fields requiered")
    )->dict:
    """
    Gets the from time  of a given employees day schedule for a given date

    Returns:
        API response as a JSON dict¨
    """
    url = f"{consts.API_ENDPOINT}/DaySchedule/GetScheduleFromTime"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    try:
        response = requests.post(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_to_time_schedule_by_employee_and_date(
    filters: GetTimeScheduleByEmployeeAndDate = Field(..., description="Filter parameters to fitler the search by, all fields requiered")
    )->dict:
    """
    Gets the from time  of a given employees day schedule for a given date

    Returns:
        API response as a JSON dict¨
    """
    url = f"{consts.API_ENDPOINT}/DaySchedule/GetScheduleToTime"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    try:
        response = requests.post(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

mcp.tool()
def get_employee_by_id(
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

@mcp.tool()
def update_employee_by_id_put(
    employee_id: UUID = Field(..., description="Employee ID"),
    query: EmployeeModel = Field(...,description="Full query object all fields optional")
    )->dict:
    """
    Update employee by employee id (put)

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employees/{employee_id}"
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_employee_by_id_post(
    employee_id: UUID = Field(..., description="Employee ID"),
    query: EmployeeModel = Field(...,description="Full query object all fields optional")
    )->dict:
    """
    Update employee by employee id (put)

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employees/{employee_id}"
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"


@mcp.tool()
def get_employees(
    filters: GetEmployees = Field(...,description="Fitler parameters to optionaly filter the search by")
    ) -> dict:
    """
    Gets employees optionaly filterd fy filter parameters

    Returns:
        Employee data as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employees"
    params = filters.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.get(
            url, 
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def create_employee(
    parameters: EmployeeCreateParams = Field(...,description="Params object all fields optional"),
    query: EmployeeCreateModel = Field(...,description="Query object all filed optional")
    )->dict:
    """
    Create a new employee

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employees"
    params = parameters.model_dump(by_alias=True,exclude_none=True)
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.post(
            url, 
            params=params,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_user_by_employee_id(
    employee_id: UUID = Field(..., description="Employee ID"),
    )->dict:
    """
    Get a user by employee id

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employees/{employee_id}/user"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_employee_image_by_id(
    id: UUID = Field(..., description="Employee ID"),
    )->dict:
    """
    Get an employee image by id

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employeeimages/{id}"
    
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def delete_employee_image_by_id(
    id: UUID = Field(..., description="Employee ID"),
    )->dict:
    """
    Delte an employee image by id

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employeeimages/{id}"
    
    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def add_or_replace_employee_image(
    query: EmployeeImageModel = Field(...,description="Query object, companyId, employeeId and iamge are requiered.")
    )->dict:
    """
    Adds or replaces an employee image

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employeeimages"
    payload = query.model_dump(by_alias=True,exclude_none=True)

    
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_employee_images(
    filters: Optional[GetEmployeeImages] = GetEmployeeImages()
    )->dict:
    """
    Get employee images optionaly filtered by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employeeimages"
    params = filters.model_dump(by_alias=True,exclude_none=True)

    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_employee_qualification_by_id(
    id: UUID = Field(..., description="Employee qulification id")
    )->dict:
    """
    Get employee qualification by id

    Returns:
        API response as JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employeequalifications/{id}"

    
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_employmee_qualification_by_id_put(
    id: UUID = Field(..., description="Employee qulification id"),
    query: EmployeeQualificationModel = Field(..., description="Query object, all fields other than id are requiered")
    )->dict:
    """
    Update employee qulatification by employee id (put)

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employeequalifications/{id}"
    payload = query.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_employee_qualification_by_id_post(
    id: UUID = Field(..., description="Employee qulification id"),
    query: EmployeeQualificationModel = Field(..., description="Query object, all fields other than id are requiered")
    )->dict:
    """
    Update employee qulatification by employee id (post)

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employeequalifications/{id}"
    payload = query.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def delete_employee_qualification_by_id(
    id: UUID = Field(..., description="Employee qulification id")
    )->dict:
    """
    Delete employee qualification by id

    Returns: 
        API response as JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employeequalifications/{id}"

    
    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_employee_qualifications(
    filters: Optional[GenericGetModel] = GenericGetModel()
    )->dict:
    """
    Get employee qualificaitons optionaly filtered by filter parameters

    Retruns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employeequalifications"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"




@mcp.tool()
def update_employment_default_accunt_by_id_put(
    id: UUID = Field(..., description="Employment deafault account id"),
    query: EmploymentDefaultAccountModel = Field(..., description="Query object, companyId, employeeId and instanceId are required")
    )->dict:
    """
    Update employment default account (put)

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentdefaultaccounts/{id}"
    payload = query.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"
@mcp.tool()

def update_employment_default_accunt_by_id_post(
    id: UUID = Field(..., description="Employement default account id"),
    query: EmploymentDefaultAccountModel = Field(..., description="Query object, companyId, employeeId and instanceId are required")
    )->dict:
    """
    Update employment default account (post)

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentdefaultaccounts/{id}"
    payload = query.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def delete_employment_default_accunt_by_id_(
    id: UUID = Field(..., description="Employment default account id")
    )->dict:
    url = f"{consts.API_ENDPOINT}/employmentdefaultaccounts/{id}"
    
    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_employment_default_accounts(
    filters: Optional[GenericGetModel] = GenericGetModel()
    )->dict:
    """
    Get employment default accounts optinaly filted by filter parameters

    Retruns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentdefaultaccounts"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def create_employment_default_accunt(
    query: EmploymentDefaultAccountModel = Field(..., description="Query object, companyId, employeeId and instanceId are required")
    )->dict:
    """
    Create employment default accoun

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentdefaultaccounts"
    payload = query.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_employment_default_account_interval_by_id(
    id: UUID = Field(..., description="Employement default accunt inteval id")
    )->dict:
    """
    Get an employment default account interval by id

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentdefaultaccountintervals/{id}"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def delete_employment_default_account_interval_by_id(
    id: UUID = Field(..., description="Employement default accunt inteval id")
    )->dict:
    """
    Delete employment defautl account intervall. 
    An employee must have at least one employment defalut account intervall.
    If deleting the last interval on an employee a new empty one will be created.

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentdefaultaccountintervals/{id}"
    
    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_employment_default_account_interval_by_id_put(
    id: UUID = Field(..., description="Employement default accunt inteval id"),
    query: EmploymentDefaultAccountIntervalModel = Field(..., description="Query object. companyId, employeeId and instanceId are required")
    )->dict:
    """
    Update an employment default account interval by id (put)

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentdefaultaccountintervals/{id}"
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_employment_default_account_interval_by_id_post(
    id: UUID = Field(..., description="Employement default accunt inteval id"),
    query: EmploymentDefaultAccountIntervalModel = Field(..., description="Query object. companyId, employeeId and instanceId are required")
    )->dict:
    """
    Update an employment default account interval by id (post)

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentdefaultaccountintervals/{id}"
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_employment_default_account_intervals(
    filters: Optional[GenericGetModel] = GenericGetModel()
    )->dict:
    """
    Get employment default account intervals optinaly filted by filter parameters

    Retruns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentdefaultaccountintervals"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def create_employment_default_account_interval(
    query: EmploymentDefaultAccountIntervalModel = Field(..., description="Query object. companyId, employeeId and instanceId are required")
    )->dict:
    """
    Create an employment default account interval

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentdefaultaccountintervals"
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_employment_documents_by_id(
    id: UUID = Field(..., description="UUID of the employement document"),

    )->dict:
    """
    Get employment document by id

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentdocuments/{id}"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def delete_employment_documents_by_id(
    id: UUID = Field(..., description="UUID of the employement document"),

    )->dict:
    """
    Delete employment document by id

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentdocuments/{id}"

    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_employment_documents_collection_by_company(
    filters: GetEmploymentDocumentCollection = Field(..., description="Filter parameters to filter the search by, companyId is requiered, all other fields optional")
    )->dict:
    """
    Get a collection of employment documents by company, optinaly filtered by filter parameters.

    Returns:
        API response as a JSON dict. Note: The returned property "title" is the filename
    """
    url = f"{consts.API_ENDPOINT}/employmentdocuments"
    params = filters.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def create_employment_document(
    document_category_id: UUID = Field(..., alias="documentCategoryId", description="UUID of the document category."),
    employee_id: UUID = Field(..., alias="employeeId", description="UUID of the employee."),
    title: Optional[str] = Field(None, description="Title of the document. If not specified the filename will be used as title."),
    file_path: str = Field(..., alias="filePath", description="Local path to the file to upload.")
) -> dict:
    """
    Uploads a document for a specific employee.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/employeedocuments"

    params = {
        "documentCategoryId": str(document_category_id),
        "employeeId": str(employee_id),
    }
    if title is not None:
        params["title"] = title

    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                url,
                params=params,
                files=files,
                timeout=consts.API_TIMEOUT
            )
        response.raise_for_status()
    except FileNotFoundError:
        raise RuntimeError(f"File not found: {file_path}")
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_employment_document_categories(
    filters: Optional[GetEmploymentDocumentCatagories] = GetEmploymentDocumentCatagories()
    )->dict:
    """
    Get employment documet categories, optinaly filted by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/documentcategories"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_employment_empty_schedule_by_id(
    id: UUID = Field(..., description="UUID of the employment empty schedule"),
    )->dict:
    """
    Get employment empy schedule by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentemptyschedules/{id}"
    
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_employment_empty_schedule_by_id(
    id: UUID = Field(..., description="UUID of the employment empty schedule"),
    allow_change_if_schedule_is_used_on_reviewed_or_transferred_days: Optional[bool] = Field(False,
        alias="allowChangeIfScheduleIsUsedOnReviewedOrTransferredDays",
        description="Whether or not to allow change if schedule is used on reviewed or transferred days. Default False"),
    query: EmptyScheduleModel = Field(...,description="Query object: companyId, employeeId and timeGroupId are requiered") 
    )->dict:
    """
    Update employment empty schedule by id

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentemptyschedules/{id}"
    params = {
        "allowChangeIfScheduleIsUsedOnReviewedOrTransferredDays": allow_change_if_schedule_is_used_on_reviewed_or_transferred_days
    }
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.put(
            url,
            params=params,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def delete_employment_empty_schedule_by_id(
    id: UUID = Field(..., description="UUID of the employment empty schedule"),
    )->dict:
    """
    Delete employment empy schedule by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentemptyschedules/{id}"
    
    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_employment_empty_schedules(
    filters: Optional[GetEmploymentEmptySchedules] = GetEmploymentEmptySchedules()
    )->dict:
    """"
    Get employment empty schedules optinaly filtered by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentemptyschedules"
    params = filters.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def create_employment_empty_schedule(
    allow_change_if_schedule_is_used_on_reviewed_or_transferred_days: Optional[bool] = Field(False,
        alias="allowChangeIfScheduleIsUsedOnReviewedOrTransferredDays",
        description="Whether or not to allow change if schedule is used on reviewed or transferred days. Default False"),
    query: EmptyScheduleModel = Field(...,description="Query object: companyId, employeeId and timeGroupId are requiered") 
    )->dict:
    """
    Create employment empty schedule 

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentemptyschedules"
    params = {
        "allowChangeIfScheduleIsUsedOnReviewedOrTransferredDays": allow_change_if_schedule_is_used_on_reviewed_or_transferred_days
    }
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.put(
            url,
            params=params,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"


@mcp.tool()
def get_employment_period_by_id(
    id: UUID = Field(..., description="UUID of the employment period"),
    )->dict:
    """
    Get employment period by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentperiods/{id}"
    
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_employment_period_by_id_put(
    id: UUID = Field(..., description="UUID of the employment period"),
    delete_timereports_after_employee_termination_date: Optional[bool] = Field(False,
        alias="deleteTimereportsAfterEmployeeTerminationDate",
        description="Remove time reports if the update sets the to date of the employment, and no employment exists in the future. No time report will be deleted if the time report is transferred to salary or if the time report is reviewed. Default false"),
    query: EmploymentPeriodModel = Field(...,description="Query object: companyId, employeeId and instanceId are requiered") 
    )->dict:
    """"
    Update the employment period by employment period id (put)

    Returns: 
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentperiods/{id}"
    params = {
        "deleteTimereportsAfterEmployeeTerminationDate": delete_timereports_after_employee_termination_date
    }
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.put(
            url,
            params=params,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_employment_period_by_id_post(
    id: UUID = Field(..., description="UUID of the employment period"),
    delete_timereports_after_employee_termination_date: Optional[bool] = Field(False,
        alias="deleteTimereportsAfterEmployeeTerminationDate",
        description="Remove time reports if the update sets the to date of the employment and no employment exists in the future. No time report will be deleted if the time report is transferred to salary or if the time report is reviewed. Default false"),
    query: EmploymentPeriodModel = Field(...,description="Query object: companyId, employeeId and instanceId are requiered") 
    )->dict:
    """"
    Update the employment period by employment period id (post)

    Returns: 
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentperiods/{id}"
    params = {
        "deleteTimereportsAfterEmployeeTerminationDate": delete_timereports_after_employee_termination_date
    }
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.post(
            url,
            params=params,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def delete_employment_period_by_id(
    id: UUID = Field(..., description="UUID of the employment period"),
    )->dict:
    """
    Delete employment period by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentperiods/{id}"
    
    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_employment_period_by_employee_id(
    employee_id: UUID = Field(..., description="UUID of the employee"),
    delete_timereports_after_employee_termination_date: bool = Field(False,
        alias="deleteTimereportsAfterEmployeeTerminationDate",
        description="Remove time reports if the update sets the to date of the employment and no employment exists in the future. No time report will be deleted if the time report is transferred to salary or if the time report is reviewed."),
    query: EmploymentPeriodModel = Field(...,description="Query object: companyId, employeeId and instanceId are requiered") 
    )->dict:
    """"
    Update the employment period for an employee given by employee id

    Returns: 
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentperiods/{employee_id}"
    params = {
        "deleteTimereportsAfterEmployeeTerminationDate": delete_timereports_after_employee_termination_date
    }
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.put(
            url,
            params=params,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_employment_periods(
    filters: Optional[GenericGetModel] = GenericGetModel()
    )->dict:
    """"
    Get employmed periods optinaly filtered by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentperiods"
    params = filters.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def create_employment_period(
    template: CreateEmploymentPeriod = Field(None, description="Whether or not to use template"),
    query: EmploymentPeriodModel = Field(...,description="Query object: companyId, employeeId and instanceId are required") 
    )->dict:
    """"
    Create employment period

    Returns: 
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentperiods"
    params = template.model_dump(by_alias=True,exclude_none=True)
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.put(
            url,
            params=params,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_employment_personal_schedule_by_id(
    id: UUID = Field(..., description="UUID of the personal employment schedule"),
    )->dict:
    """
    Get personal emplotment schedule by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentpersonalschedules/{id}"
    
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def update_employment_personal_schedule_by_id_put(
    id: UUID = Field(..., description="UUID of the personal employment schedule"),
    query: EmploymentPersonalScheduleModel = Field(..., description="Query Object, companyId, employeeId, instanceId personalScheduleId and timeGroupId are requiered"),
    )->dict:
    """
    Update personal emplotment schedule by id (put)

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentpersonalschedules/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def update_employment_personal_schedule_by_id_post(
    id: UUID = Field(..., description="UUID of the personal employment schedule"),
    query: EmploymentPersonalScheduleModel = Field(..., description="Query Object, companyId, employeeId, instanceId personalScheduleId and timeGroupId are requiered"),
    )->dict:
    """
    Update personal emplotment schedule by id (post)

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentpersonalschedules/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()


@mcp.tool()
def delete_employment_personal_schedule_by_id(
    id: UUID = Field(..., description="UUID of the personal employment schedule"),
    )->dict:
    """
    Delete personal emplotment schedule by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentpersonalschedules/{id}"
    
    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_employment_personal_schedules(
    filters: GenericGetModel = Field(GenericGetModel(),description="Fitler parameters to fitler the search by all feilds optional")
    )->dict:
    """"
    Get employment personal schedules optinaly filtered by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentpersonalschedules"
    params = filters.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def create_employment_personal_schedule(
    allow_change_if_schedule_is_used_on_reviewed_or_transferred_days: Optional[bool] = Field(False,
        alias="allowChangeIfScheduleIsUsedOnReviewedOrTransferredDays",
        description="Whether or not to allow change if schedule is used on reviewed or transferred days. Default False"),
    query: EmploymentPersonalScheduleModel = Field(..., description="Query Object, companyId, employeeId, instanceId personalScheduleId and timeGroupId are requiered"),
    )->dict:
    """"
    Create employment personal schedule

    Returns: 
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentpersonalschedules"
    params = {
        "allowChangeIfScheduleIsUsedOnReviewedOrTransferredDays": allow_change_if_schedule_is_used_on_reviewed_or_transferred_days
    }
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)

    try:
        response = s.post(
            url,
            params=params,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_employment_public_schedule_by_id(
    id: UUID = Field(..., description="UUID of the public employment schedule"),
    )->dict:
    """
    Get public emplotment schedule by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentpublicschedules/{id}"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def update_employment_public_schedule_by_id_put(
    id: UUID = Field(..., description="UUID of the public employment schedule"),
    query: EmploymentPublicScheduleModel = Field(..., description="Query Object, companyId, employeeId, instanceId publicScheduleId and timeGroupId are requiered"),
    )->dict:
    """
    Update public employment schedule by id (put)

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentpublicschedules/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def update_employment_public_schedule_by_id_post(
    id: UUID = Field(..., description="UUID of the public employment schedule"),
    query: EmploymentPublicScheduleModel = Field(..., description="Query Object, companyId, employeeId, instanceId publicScheduleId and timeGroupId are requiered"),
    )->dict:
    """
    Update public emplotment schedule by id (post)

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentpublicschedules/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def delete_employment_public_schedule_by_id(
    id: UUID = Field(..., description="UUID of the public employment schedule"),
    )->dict:
    """
    Delete public employment schedule by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentpublicschedules/{id}"
    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_employment_public_schedules(
    filters: GetPublicEmploymentSchedules = Field(GetPublicEmploymentSchedules(),description="Filter parameters to filter the search by all fields optional")
    )->dict:
    """"
    Get public employment schedules optionally filtered by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentpublicschedules"
    params = filters.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def create_employment_public_schedule(
    allow_change_if_schedule_is_used_on_reviewed_or_transferred_days: Optional[bool] = Field(False,
        alias="allowChangeIfScheduleIsUsedOnReviewedOrTransferredDays",
        description="Whether or not to allow change if schedule is used on reviewed or transferred days. Default False"),
    query: EmploymentPublicScheduleModel = Field(..., description="Query Object, companyId, employeeId, instanceId publicScheduleId and timeGroupId are requiered"),
    )->dict:
    """"
    Create employment public schedule

    Returns: 
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentpublicschedules"
    params = {
        "allowChangeIfScheduleIsUsedOnReviewedOrTransferredDays": allow_change_if_schedule_is_used_on_reviewed_or_transferred_days
    }
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)

    try:
        response = s.post(
            url,
            params=params,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_employment_rate_by_id(
    id: UUID = Field(..., description="UUID of the employment rate"),
    )->dict:
    """
    Get employment rate by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentrates/{id}"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def update_employment_rate_by_id_put(
    id: UUID = Field(..., description="UUID of the employment rate"),
    query: EmploymentRateModel = Field(..., description="Query object, companyId, empoyeeId and instanceId are required"),
    )->dict:
    """
    Update employment rate by id (put)

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentrate/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def update_employment_rate_by_id_post(
    id: UUID = Field(..., description="UUID of the employment rate"),
    query: EmploymentRateModel = Field(..., description="Query object, companyId, empoyeeId and instanceId are required"),
    )->dict:
    """
    Update employment rate by id (post)

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentrate/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def delete_employment_rate_by_id(
    id: UUID = Field(..., description="UUID of the employment rate"),
    )->dict:
    """
    Delete employment rate by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentrates/{id}"

    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def batch_update_employment_rate_by_employee_id(
    employee_id: UUID = Field(..., description="UUID of the employee"),
    query: List[EmploymentRateModel] = Field(..., description="Query object, companyId, empoyeeId and instanceId are required"),
    )->dict:
    """
    Batch update employment rate for an employee given by employee id

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employees/{employee_id}/employmentrates"

    employment_rates = [
        EmploymentRateModel(**employment_rate) if isinstance(employment_rate, dict) else employment_rate
        for employment_rate in query
    ]

    payload = [employment_rate.model_dump(mode="json", by_alias=True, exclude_none=True) for employment_rate in employment_rates]

    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_employment_rates(
    filters: GenericGetModel = Field(GenericGetModel(),description="Fitler parameters to fitler the search by all feilds optional")
    )->dict:
    """"
    Get employment rates optionaly filtered by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentates"
    params = filters.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def create_employment_rate(
    query: EmploymentRateModel = Field(..., description="Query object, companyId, empoyeeId and instanceId are required"),
    )->dict:
    """
    Create employment rate

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentrate"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_employment_templates_by_company_id(
    company_id: UUID = Field(..., description="UUID of the company"),
    page_params: PageModel = Field(PageModel(),description="Page parameters")
    )->dict:
    """
    Get employment templates by company id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/companies/{company_id}/employmenttemplate"
    params = page_params.model_dump(by_alias=True,exclude_none=True)
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_employment_title_by_id(
    id: UUID = Field(..., description="UUID of the employment tile"),
    )->dict:
    """
    Get employment title by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmenttitles/{id}"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def update_employment_title_by_id_put(
    id: UUID = Field(..., description="UUID of the employment title"),
    query: EmploymentTitleModel = Field(..., description="Query object, code, companyId, and name are required"),
    )->dict:
    """
    Update employment title by id (put)

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentitle/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def update_employment_title_by_id_post(
    id: UUID = Field(..., description="UUID of the employment title"),
    query: EmploymentTitleModel = Field(..., description="Query object, code, companyId, and name are required"),
    )->dict:
    """
    Update employment title by id (post)

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentitle/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def delete_employment_title_by_id(
    id: UUID = Field(..., description="UUID of the employment tile"),
    )->dict:
    """
    Delete employment title by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmenttitles/{id}"

    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_employment_titles(
    filters: GetEmplploymentTitles = Field(GetEmplploymentTitles(),description="Fitler parameters to fitler the search by all feilds optional")
    )->dict:
    """"
    Get employment titles optionaly filtered by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmenttitles"
    params = filters.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def create_employment_title(
    query: EmploymentTitleModel = Field(..., description="Query object, code, companyId, and name are required"),
    )->dict:
    """
    Create employment title

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentitle"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_employment_type_by_id(
    id: UUID = Field(..., description="UUID of the employment type"),
    )->dict:
    """
    Get employment type by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmenttypes{id}"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()


@mcp.tool()
def get_employment_types(
    filters: GetEmploymentTypes = Field(GetEmploymentTypes(),description="Fitler parameters to fitler the search by all feilds optional")
    )->dict:
    """"
    Get employment titles optionaly filtered by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmenttitles"
    params = filters.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_employment_vacation_by_id(
    id: UUID = Field(..., description="UUID of the employment vacation"),
    )->dict:
    """
    Get employment vaccations by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmenvacations{id}"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def update_employment_vaction_by_id_put(
    id: UUID = Field(..., description="UUID of the employment vacation"),
    query: Optional[EmploymentVacationModel] = Field(EmploymentVacationModel(), description="Query object all fields are optional"),
    )->dict:
    """
    Update employment vacation by id (put)

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentvacation/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def update_employment_vaction_by_id_post(
    id: UUID = Field(..., description="UUID of the employment vacation"),
    query: Optional[EmploymentVacationModel] = Field(EmploymentVacationModel(), description="Query object all fields are optional"),
    )->dict:
    """
    Update employment vacation by id (post)

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentvacation/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_employment_vacations(   
    filters: Optional[GenericGetModel] = Field(GenericGetModel(), description="Parameters to filter the search by all feilds optional")
    )->dict:

    """
    Get employment vaccations optionaly filtered by filter parameters

    Retruns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentvaccations"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_employment_vacations_quotas(
    filters: Optional[GenericGetModel] = Field(GenericGetModel(), description="Parameters to filter the search by all feilds optional")
    )->dict:
    """
    Get employment vacation quotas optionaly filtered by filter parameters

    Retruns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentvaccationquoatas"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_employment_vehicle_by_id(
    id: UUID = Field(..., description="UUID of the employment vehicle"),
    )->dict:
    """
    Get employment vehicle by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentvehicle/{id}"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def update_employment_vehicle_by_id(
    id: UUID = Field(..., description="UUID of the employment vehicle"),
    query: Optional[EmploymentVehicleModel] = Field(..., description="CompanyID and EmployeeID are required, all other feilds optional"),
    )->dict:
    """
    Update employment vehicle by id 

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentvehicle/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def delete_employment_vehicle_by_id(
    id: UUID = Field(..., description="UUID of the employment vehicle"),
    )->dict:
    """
    Delete employment vehicle by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentvehicle/{id}"

    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_employment_vehciles(   
    filters: Optional[GetEmploymentVehicles] = Field(GetEmploymentVehicles(), description="Parameters to filter the search by all feilds optional")
    )->dict:

    """
    Get employment vechicles optionaly filtered by filter parameters

    Retruns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employmentvehicle"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def create_employment_vehicle(
    query: EmploymentVehicleModel = Field(..., description="CompanyID and EmployeeID are required, all other feilds optional"),
    )->dict:
    """
    Create employment vehicle

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentvechicle"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_company_information(
    instance: str = Field(INSTANCE, description="Domain name"),
    start_range: int = Field(..., alias="startRange", description="Company Number. Start of the range, the start value is included in the result."),
    end_range: int = Field(..., alias="endRange", description="Company Number. End of the range, the end value is included in the result.")
    )->dict:
    """
    Get company information for companies with company number in the given range for a given instance. If no instance is provided, defaults to the default-domain instance.

    Returns:
        A API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/GetCompanyInformation/GetCompanyInformation"
    params = {
        "instance": instance,
        "startRange": start_range,
        "endRange": end_range
    }

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
          return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_hr_form_document_template_by_id(
    id: UUID = Field(..., description="UUID of the HR form document template"),
    )->dict:
    """
    Get HR form document template by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/hrforms/{id}/documenttemplate"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def delete_hr_form__by_id(
    id: UUID = Field(..., description="UUID of the HR form"),
    )->dict:
    """
    Delete HR form by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/hrforms/{id}"

    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def update_hr_form_by_id(
    id: UUID = Field(..., description="UUID of the HR form to update."),
    file_path: str = Field(..., alias="filePath", description="Local path to the file to upload. Optional."),
    body: HrFormModel = Field(..., description="JSON representation of the HR form to update.")
    ) -> dict:
    """
    Updates an HR form by id. Sends file and form data using multipart/form-data.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/hrforms/{id}"

    if isinstance(body, dict):
        body = HrFormModel(**body)

    multipart_data = {
        "body": (None, body.model_dump_json(by_alias=True, exclude_none=True), "application/json")
    }

    try:
        file = open(file_path, "rb")
        multipart_data["file"] = (file_path, file, "application/octet-stream")
    except FileNotFoundError:
        raise RuntimeError(f"File not found: {file_path}")

    try:
        response = requests.put(
            url,
            files=multipart_data,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    try:
        file.close()
    except:
        pass
    return response.json()

@mcp.tool()
def get_hr_form_by_id(
    id: UUID = Field(..., description="UUID of the HR form"),
    )->dict:
    """
    Get HR form by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/hrforms/{id}"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def create_hr_form(
    file_path: str = Field(..., alias="filePath", description="Local path to the file to upload. Optional."),
    body: HrFormModel = Field(..., description="JSON representation of the HR form to create.")
    ) -> dict:
    """
    Creates a new HR form. Sends file and form data using multipart/form-data.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/api/hrforms"

    if isinstance(body, dict):
        body = HrFormModel(**body)

    multipart_data = {
        "body": (None, body.model_dump_json(by_alias=True, exclude_none=True), "application/json")
    }

    try:
        file = open(file_path, "rb")
        multipart_data["file"] = (file_path, file, "application/octet-stream")
    except FileNotFoundError:
        raise RuntimeError(f"File not found: {file_path}")

    try:
        response = requests.post(
            url,
            files=multipart_data,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    try:
        file.close()
    except:
        pass
    return response.json()

@mcp.tool()
def get_hr_forms(   
    filters: Optional[GetHrForms] = GetHrForms()
    )->dict:

    """
    Get HR forms optionaly filtered by filter parameters

    Retruns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/hrforms"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"
    
@mcp.tool()
def import_company(
    instance: Optional[str] = Field(INSTANCE, description="Domain name. If not provided defaults to the default domain."),
    query: NewCompanyViewModel = Field(..., description="Query object, companyName, companyNumber, copySettingsFromExistingCompany, and customerInstanceDomain are required, if customerInstanceDomain is not provided, defauls to the default domain"),
    )->dict:
    """
    Creates and adds a company to the database.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/ImportCompany/Post"
    params = {
        instance: instance
    }
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.post(
            url,
            params=params,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"
    
@mcp.tool()
def import_company_get_example_data(
    instance: Optional[str] = Field(INSTANCE, description="Domain name. If not provided defaults to the default domain."),
    )->dict:
    """
    Creates and returns an example on how indata could look when using the POST-method.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/ImportCompany/GetExampleData"
    params = {
        instance: instance
    }
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"


@mcp.tool()
def get_imported_trip_by_id(
    id: UUID = Field(..., description="UUID of the imported trip"),
    )->dict:
    """
    Get imported trip by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/importedtrips/{id}"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_imported_trips_by_employee_id(
    employee_id: UUID = Field(..., description="UUID of the employee"),
    filters: GetImportedTripsByEmployeeId = Field(GetImportedTripsByEmployeeId(), description="Filter parameters to filter the search, all fields are optional" )
    )->dict:
    """
    Get imported trips by employee id, optionaly filtered by filter parameters.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employees/{employee_id}/importedtrips"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def create_imported_trip(
    query: ImportedTripModel = Field(..., description="employeeId, fromDateTime, toDateTime are required, all other fields are optional"),
    )->dict:
    """
    Create imported trip. Must be unique in that two trips cannot have the same employeeId, fromDateTime and toDateTime.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/importedtrips"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def batch_create_imported_trip(
    query: List[ImportedTripModel] = Field(..., description="List of imported trips to create."),
) -> dict:
    """
    Create imported trips in batch. Each trip must be unique in that two trips cannot have the same employeeId, fromDateTime and toDateTime.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/importedtrips"

    trips = [
        ImportedTripModel(**trip) if isinstance(trip, dict) else trip
        for trip in query
    ]

    payload = [trip.model_dump(mode="json", by_alias=True, exclude_none=True) for trip in trips]

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_invocing_basis_by_billing_release_id(
    billing_release_id: UUID = Field(..., description="UUID of the billing release"),
    page_params: PageModel = Field(PageModel(), description="Page parameters"),
    include_exported: Optional[bool] = Field(False, description="Whether to include exported invoicing basis in the result. Optional, defaults to false."),
    include_all_accounts: Optional[bool] = Field(False, description="Whether to include invoicing basis for all accounts in the result. Optional, defaults to false.")
    )->dict:
    """
    Get invoicing basis by billing release id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/invoicingbasis"
    parapms = {
        "billingReleaseId": billing_release_id,
        "pageNumber": page_params.page_number,
        "pageSize": page_params.page_size,
        "includeExported": include_exported,
        "includeAllAccounts": include_all_accounts
    }
    
    try:
        response = requests.post(
            url,
            params=parapms,
            timeout=consts.API_TIMEOUT
        )
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_next_of_kin_by_id(
    id: UUID = Field(..., description="UUID of the next of kin"),
    )->dict:
    """
    Get next of kin by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/nextofkin/{id}"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def update_next_of_kin_by_id_put(
    id: UUID = Field(...,description="UUID of the next of kin"),
    query: NextOfKinModel = Field(...,description="Full query object")
    )->dict:
    """
    Update a next of kin by id (put)

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/nextofkin/{id}"
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_next_of_kin_by_id_post(
    id: UUID = Field(...,description="UUID of the next of kin"),
    query: NextOfKinModel = Field(...,description="Full query object")
    )->dict:
    """
    Update a next of kin by id (post)

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/nextofkin/{id}"
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def delete_next_of_kin_by_id(
    id: UUID = Field(..., description="UUID of the next of kin"),
    )->dict:
    """
    Delete next of kin by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/nextofkin/{id}"

    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_next_of_kins(
    filters: Optional[GenericGetModel] = Field(GenericGetModel(), description="Parameters to filter the search by all feilds optional")
    )->dict:
    """
    Get next of kins optionaly filtered by filter parameters

    Retruns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/nextofkin"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def create_next_of_kin(
    query: NextOfKinModel = Field(...,description="Full query object")
    )->dict:
    """
    Create a next of kin

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/nextofkin"
    payload = query.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_next_of_kin_relationship_by_id(
    id: UUID = Field(..., description="UUID of the next of kin"),
    )->dict:
    """
    Get next of kin relationship by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/nextofkinrelationship/{id}"

    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_next_of_kin_relationships(
    page_params: PageModel = Field(PageModel(), description="Page parameters"),
    )->dict:
    """
    Get next of kin relationship by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/nextofkinrelationship"
    params = page_params.model_dump(by_alias=True, exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_overtime_by_user_id(
    user_id: UUID = Field(..., description="UUID of the user"),
    instance: Optional[str] = Field(INSTANCE, alias="instans", description="Domain name. If not provided defaults to the default domain."),
    date: Optional[datetime] = Field(datetime.now(), description="Optional date to get overtime markers for. If not given, current date will be used.")
    )->dict:
    """
    Get overtime by user id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/overtime/GetByUserID"

    params = {
        "userId": user_id,
        "instans": instance,
        "date": date
    }

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_overtime_by_employee_id(
    employee_id: UUID = Field(..., description="UUID of the employee"),
    instance: Optional[str] = Field(INSTANCE, alias="instans", description="Domain name. If not provided defaults to the default domain."),
    date: Optional[datetime] = Field(datetime.now(), description="Optional date to get overtime markers for. If not given, current date will be used.")
    )->dict:
    """
    Get overtime by employee id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/overtime/GetByEmployeeID"

    params = {
        "employeeId": employee_id,
        "instans": instance,
        "date": date
    }

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_own_assessment_fields(
    filters: Optional[GetOwnFieldModel] = Field(GetOwnFieldModel(), description="Parameters to filter the search by all feilds optional")
    )->dict:
    """
    Get own assessment fields optionaly filtered by filter parameters

    Returns
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/ownassessmentfields"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    
@mcp.tool()
def get_own_assessment_field_value_by_id(
    id: UUID = Field(..., description="UUID of the own assessment field value"),
    )->dict:
    """
    Get own assessment field value by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/ownassessmentfieldvalues/{id}"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def update_own_assessment_field_value_by_id_put(
    id: UUID = Field(..., description="UUID of the own assessment field value"),
    query: OwnAssessmentFieldValueModel = Field(..., description="Full query object to update the own assessment field value with")
    )->dict:
    """
    Update own assessment field value by id (put).

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/ownassessmentfieldvalues/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def update_own_assessment_field_value_by_id_post(
    id: UUID = Field(..., description="UUID of the own assessment field value"),
    query: OwnAssessmentFieldValueModel = Field(..., description="Full query object to update the own assessment field value with")
    )->dict:
    """
    Update own assessment field value by id (post).

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/ownassessmentfieldvalues/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)

    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def delete_own_assessment_field_value_by_id(
    id: UUID = Field(..., description="UUID of the own assessment field value"),
    )->dict:
    """
    Delete own assessment field value by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/ownassessmentfieldvalues/{id}"
    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def create_own_assessment_field_value(
    query: OwnAssessmentFieldValueModel = Field(..., description="Full query object to update the own assessment field value with")
    )->dict:
    """
    Create a new own assessment field value.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/ownassessmentfieldvalues"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def get_own_assessment_field_values(   
    filters: Optional[GenericGetModel] = Field(GenericGetModel(), description="Parameters to search the assessment field values by, all fields optional")
    )->dict:
    """
    Get own assessment field values optionaly filtered by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/ownassessmentfieldvalues"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_own_date_fields(   
    filters: Optional[GetOwnFieldModel] = Field(GetOwnFieldModel(), description="Parameters to search the assessment field values by, all fields optional")
    )->dict:
    """
    Get own date fields optionaly filtered by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/owndatefields"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_own_date_field_value_by_id(
    id: UUID = Field(..., description="UUID of the own date field value"),
    )->dict:
    """
    Get own date field value by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/owndatefieldvalues/{id}"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def update_own_date_field_value_by_id_put(
    id: UUID = Field(..., description="UUID of the own date field value"),
    query: OwnDateFieldValueModel = Field(..., description="Full query object to update the own date field value with")
    )->dict:
    """
    Update own date field value by id (put).

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/owndatefieldvalues/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    
@mcp.tool()
def update_own_date_field_value_by_id_post(
    id: UUID = Field(..., description="UUID of the own date field value"),
    query: OwnDateFieldValueModel = Field(..., description="Full query object to update the own date field value with")
    )->dict:
    """
    Update own date field value by id (post).

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/owndatefieldvalues/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def delete_own_date_field_value_by_id(
    id: UUID = Field(..., description="UUID of the own date field value"),
    )->dict:
    """
    Delete own date field value by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/owndatefieldvalues/{id}"
    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def get_own_date_field_values(   
    filters: Optional[GenericGetModel] = Field(GenericGetModel(), description="Parameters to search the assessment field values by, all fields optional")
    )->dict:
    """
    Get own date field values optionaly filtered by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/owndatefieldvalues"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"
    
@mcp.tool()
def create_own_date_field_value(
    query: OwnDateFieldValueModel = Field(..., description="Full query object to update the own date field value with")
    )->dict:
    """
    Create own date field value. Will update existing date field value if date field already has value.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/owndatefieldvalues/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()


@mcp.tool()
def get_own_numerical_fields(   
    filters: Optional[GetOwnFieldModel] = Field(GetOwnFieldModel(), description="Parameters to search the assessment field values by, all fields optional")
    )->dict:
    """
    Get own numerical fields optionaly filtered by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/ownnumericalfields"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_own_numerical_field_value_by_id(
    id: UUID = Field(..., description="UUID of the own numerical field value"),
    )->dict:
    """
    Get own numerical field value by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/ownnumericalfieldvalues/{id}"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def update_own_numerical_field_value_by_id_put(
    id: UUID = Field(..., description="UUID of the own numerical field value"),
    query: OwnNumericalFieldValueModel = Field(..., description="Full query object to update the own numerical field value with")
    )->dict:
    """
    Update own numerical field value by id (put).

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/ownnumericalfieldvalues/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def update_own_numerical_field_value_by_id_post(
    id: UUID = Field(..., description="UUID of the own numerical field value"),
    query: OwnNumericalFieldValueModel = Field(..., description="Full query object to update the own numerical field value with")
    )->dict:
    """
    Update own numerical field value by id (post).

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/ownnumericalfieldvalues/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def delete_own_numerical_field_value_by_id(
    id: UUID = Field(..., description="UUID of the own numerical field value"),
    )->dict:
    """
    Delete own numerical field value by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/ownnumericalfieldvalues/{id}"
    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def get_own_numerical_field_values(   
    filters: Optional[GenericGetModel] = Field(GenericGetModel(), description="Parameters to search the assessment field values by, all fields optional")
    )->dict:
    """
    Get own numerical field values optionaly filtered by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/ownnumericalfieldvalues"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"
        
@mcp.tool()
def create_own_numerical_field_value(
    query: OwnNumericalFieldValueModel = Field(..., description="Full query object to update the own numerical field value with")
    )->dict:
    """
    Create new own numerical field value.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/ownnumericalfieldvalues"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def get_own_text_fields(   
    filters: Optional[GetOwnFieldModel] = Field(GetOwnFieldModel(), description="Parameters to search the assessment field values by, all fields optional")
    )->dict:
    """
    Get own text fields optionaly filtered by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/owntextfields"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"
    
@mcp.tool()
def get_own_text_field_value_by_id(
    id: UUID = Field(..., description="UUID of the own text field value"),
    )->dict:
    """
    Get own text field value by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/owntextfieldvalues/{id}"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def update_own_text_field_value_by_id_put(
    id: UUID = Field(..., description="UUID of the own text field value"),
    query: OwnTextFieldValueModel = Field(..., description="Full query object to update the own text field value with")
    )->dict:
    """
    Update own text field value by id (put).

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/owntextfieldvalues/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def update_own_text_field_value_by_id_post(
    id: UUID = Field(..., description="UUID of the own text field value"),
    query: OwnTextFieldValueModel = Field(..., description="Full query object to update the own text field value with")
    )->dict:
    """
    Update own text field value by id (post).

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/owntextfieldvalues/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def delete_own_text_field_value_by_id(
    id: UUID = Field(..., description="UUID of the own text field value"),
    )->dict:
    """
    Delete own text field value by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/owntextfieldvalues/{id}"
    try:
        response = s.delete(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def get_own_text_field_values(   
    filters: Optional[GenericGetModel] = Field(GenericGetModel(), description="Parameters to search the assessment field values by, all fields optional")
    )->dict:
    """
    Get own text field values optionaly filtered by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/owntextfieldvalues"
    params = filters.model_dump(by_alias=True,exclude_none=True)
    
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"


@mcp.tool()
def create_own_text_field_value(
    query: OwnTextFieldValueModel = Field(..., description="Full query object to update the own text field value with")
    )->dict:
    """
    Create a new own text field value.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/owntextfieldvalues"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def get_paycodes_with_staff_category_settings(
    filters: Optional[GetPaycodesWithStaffCategorySettings] = GetPaycodesWithStaffCategorySettings()
    )->dict:
    """
    Get pay codes with staff category settings, optionally filtered by filter parameters.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/paycodes"
    params = filters.model_dump(by_alias=True, exclude_none=True)
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def get_paycode_by_id(
    id: UUID = Field(..., description="UUID of the pay code"),
    )->dict:
    """
    Get pay code by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/paycodes/{id}"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()


@mcp.tool()
def get_payment_group_by_id(
    id: UUID = Field(..., description="UUID of the payment group"),
    )->dict:
    """
    Get payment group by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/paymentgroups/{id}"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def get_payment_groups(
    filters: Optional[GetPaymentGroups] = Field(GetPaymentGroups(), description="Parameters to filter the search by all feilds optional")
    )->dict:
    """
    Get payment groups, optionally filtered by filter parameters.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/paymentgroups"
    params = filters.model_dump(by_alias=True, exclude_none=True)
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    
@mcp.tool()
def get_payroll_runs(
    filters: Optional[GetPayrollRuns] = Field(GetPayrollRuns(), description="Parameters to filter the search by all feilds optional")
)-> dict:
    """
    Get payroll runs.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/payrollruns"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def get_payroll_run_by_id(
    id: UUID = Field(..., description="UUID of the payroll run"),
    )->dict:
    """
    Get payroll run by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/payrollruns/{id}"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def get_payroll_run_employments(
    filters: Optional[GetPayrollRunEmployments] = Field(GetPayrollRunEmployments(), description="Parameters to filter the search by all feilds optional")
)-> dict:
    """
    Get payroll run employments.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/payrollrunemployees"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def get_payroll_run_employee_by_id(
    id: UUID = Field(..., description="UUID of the paycode id"),
    )->dict:
    """
    Get payroll run employee by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/payrollemploymentss/{id}"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def get_payroll_run_transactions(
    filters: Optional[GetPayrollRunTransactions] = Field(GetPayrollRunTransactions(), description="Parameters to filter the search by all feilds optional")
)-> dict:
    """
    Get payroll run transactions, optionally filtered by filter parameters.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/payrollruntransactions"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    
@mcp.tool()
def get_payroll_run_transaction_by_id(
    id: UUID = Field(..., description="UUID of the paycode id"),
    )->dict:
    """
    Get payroll run transaction by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/payrollruntransactions/{id}"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def get_payroll_run_transaction_account_collections(
    filters: Optional[GetPayrollRunTransactions] = Field(GetPayrollRunTransactions(), description="Parameters to filter the search by all feilds optional")
)-> dict:
    """
    Get payroll run transactions, optionally filtered by filter parameters.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/payrollruntransactionaccounts"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def get_payroll_run_transaction_account_collectioion_by_id(
    id: UUID = Field(..., description="Payroll run transaction account collection id. (UUID)"),
    )->dict:
    """
    Get payroll run transaction by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/payrollruntransactionaccounts/{id}"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def get_settled_payslip_by_payroll_run_employee_id(
    payroll_run_employee_id: UUID = Field(..., alias="payrollrunEmployeeId", description="UUID of the payroll run employee."),
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    ) -> dict:
    """
    Get settled payslip by payroll run employee id.

    Returns:
        Settled API resonse as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/payslip/{payroll_run_employee_id}"
    params = {"companyId": company_id}

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def get_pension_and_insurance_setting_by_employee_id(
    employee_id: UUID = Field(..., alias="id", description="Employee ID (UUID)"),
    )->dict:
    """
    Get payroll run transaction by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employees/{employee_id}/pensionandinsurances"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()


@mcp.tool()
def update_pension_and_insurance_setting_by_employee_id_put(
    employee_id: UUID = Field(..., alias="id", description="Employee ID (UUID)"),
    query: PensionAndInsuranceModel = Field(..., description="Full query object to update the pension and insurance setting with")
    )->dict:
    """
    Update pension and insurance setting by employee id (put).

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employees/{employee_id}/pensionandinsurances"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    
@mcp.tool()
def update_pension_and_insurance_setting_by_employee_id_post(
    employee_id: UUID = Field(..., alias="id", description="Employee ID (UUID)"),
    query: PensionAndInsuranceModel = Field(..., description="Full query object to update the pension and insurance setting with")
    )->dict:
    """
    Update pension and insurance setting by employee id (post).

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employees/{employee_id}/pensionandinsurances"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def get_pension_and_insurance_settings(
    filters: Optional[GetPensionAndInsuranceSettings] = Field(GetPensionAndInsuranceSettings(), description="Parameters to filter the search by all feilds optional")
)-> dict:
    """
    Get pension and insurance settings, optionally filtered by filter parameters.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employees/pensionandinsurances"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    
@mcp.tool()
def get_permissions_to_commpanies_by_user_id(
    user_id: UUID = Field(..., alias="userId", description="UUID of the user")
    )-> dict:
    """
    Get permissions to companies by user id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/users/{user_id}/permissions"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()

@mcp.tool()
def get_personal_schedule_by_id(
    id: UUID = Field(..., description="UUID of the personal  schedule"),
    )->dict:
    """
    Get personal schedule by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/personalschedules/{id}"
    
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_personal_schedules(
    filters: GenericGetModel = Field(GenericGetModel(),description="Fitler parameters to fitler the search by all feilds optional")
    )->dict:
    """"
    Get  personal schedules optinaly filtered by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/personalschedules"
    params = filters.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_employee_presence_by_company(
    query: GetEmployeePresenceByCompany = Field(..., description="Full query object. company_id is required. All other fields are optional"),
    filters: PresenceSelectionFilterModel = Field(PresenceSelectionFilterModel(), description="Filter parameters to filter the search by, all fields optional")
    )->dict:
    """
    Get employee presence for a given company.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/company/{query.company_id}/presence"
    payload = filters.model_dump(by_alias=True, exclude_none=True)
    try:
        response = s.get(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_project_by_id(
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
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def update_project_by_id(
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

@mcp.tool()
def delete_project_by_id(
    project_id: UUID = Field(..., description="UUID of the project.")
) -> dict:
    """
    Deletes a project by ID

    Returns:
        Project data as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/projects/{project_id}"

    try:
        response = s.delete(url, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_reported_hours_on_projects(
    query: GetReportedHoursOnProjects = Field(..., description="Full query object. accountdistributionid, status, fromDate and toDate are required. All other fields are optional")
    )->dict:
    """
    Get reported hours on projects for a given account distribution id, status and date range. Optinaly fitltered by additional fitler parameters.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/accountdistributions/{query.account_distribution_id}/ReportedHours"
    params = query.model_dump(by_alias=True, exclude_none=True, exclude={"account_distribution_id"})
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_project_by_account_distribution_id(
    account_distribution_id: UUID = Field(..., description="UUID of the account distribution.")
) -> dict:
    """
    Gets project information by account distribution ID

    Returns:
        Project data as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/accountdistributions/{account_distribution_id}/projects"

    try:
        response = s.get(url, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def batch_post_project_by_account_distribution_id(
    account_distribution_id: UUID = Field(..., description="UUID of the account distribution."),
    projects: List[ProjectModel] = Field(
        ...,
        description=(
            "List of project objects. code and name are required for each project. All other fields are optional "
            "and only sent if explicitly provided. Enum fields are integers — see field "
            "descriptions for valid values."
        ),
    ),
) -> dict:
    """
    Updates a list of projects by their IDs.
    The request body must include code and name at minimum.
    All other fields are optional and will only be included in the payload if set.
 
    Returns:
        Updated project data as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/accountdistributions/{account_distribution_id}/projects"
 
    projects = [
        ProjectModel(**project) if isinstance(project, dict) else project
        for project in projects
    ]

    payload = [project.model_dump(mode="json", by_alias=True, exclude_none=True) for project in projects]
 
    try:
        response = s.put(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=consts.API_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed {e}\n{response.text}")
    return response.json() if response.content else {"status": "ok"}

@mcp.tool()
def get_projects(
    company: str = Field(..., description="Company number."),
    filters: GetProjects = GetProjects()
    )->dict:
    """
    Get projects, optionally filtered by filter parameters.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/projects"
    params = filters.model_dump(by_alias=True, exclude_none=True)
    params["company"] = company
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_public_schedule_by_id(
    id: UUID = Field(..., description="UUID of the public schedule"),
    )->dict:
    """
    Get public schedule by id

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/publicschedules/{id}"
    
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_public_schedules(
    filters: GenericGetModel = Field(GenericGetModel(),description="Fitler parameters to fitler the search by all feilds optional")
    )->dict:
    """"
    Get  public schedules optinaly filtered by filter parameters

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/publicschedules"
    params = filters.model_dump(by_alias=True,exclude_none=True)

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_public_travel_claims(
    filters: GetTravelClaims = GetTravelClaims()
    )->dict:
    """
    Filter public travel claims by specified criteria..

    Returns:
        A JSON dict containing the list of travel claims.
     """
    url = f"{consts.API_ENDPOINT}/travelclaim"
    params = filters.model_dump(by_alias=True, exclude_none=True, mode="json")
    print(params)
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_public_travel_claim_attachment_by_id(
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
        return f"API request failed: {e}\n{response.text}"
    
    content_disposition = response.headers.get("Content-Disposition", "")
    filename = content_disposition.split("filename=")[-1].strip('"') if "filename=" in content_disposition else str(id)

    return {
        "filename": filename,
        "content_type": response.headers.get("Content-Type", "application/octet-stream"),
        "content_base64": base64.b64encode(response.content).decode("utf-8")
    }


@mcp.tool()
def get_travel_claim_audit_levels_by_company_id(
    company_id: UUID = Field(..., description="UUID of the company."),
    )->dict:
    """
    Get travel claim audit levels by company ID.

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_qualifications(
    filters: GetQualifications = GetQualifications()
    )->dict:
    """
    Gets qualifications optinaly filtered by filter parameters.

    Returns:
        A JSON dict containing the list of qualifications.
    """
    url = f"{consts.API_ENDPOINT}/qualifications"
    try:
        response = s.get(
            url,
            params=filters.model_dump(by_alias=True, exclude_none=True),
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_reminders_by_user_id(
    user_id: str = Field(..., description="Alias/Alias user-ID or Username/User-ID of a user."),
    companynumber: str = Field(None, description="Company number. If empty the users default company will be used."),
    instance: str = Field(INSTANCE, description="Domain name"),
    )->dict:
    """
    Get all active reminders for the given user.

    Returns:
        API resonse as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/Reminder/GetReminders"
    params = {
        "userId": user_id,
        "companynumber": companynumber,
        "instance": instance
    }
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_resignation_cause_by_id(
    id: UUID = Field(..., description="UUID of the resignation cause.")
    )->dict:
    """
    Get resignation cause  by id.

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/resignationcauses/{id}"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def update_resignation_cause_by_id_put(
    id: UUID = Field(..., description="UUID of the resignation cause."),
    query: ResignationCauseModel = Field(ResignationCauseModel(), description="Full query object to update the resignation cause with")
    )->dict:
    """
    Update resignation cause  by id (put).

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/resignationcauses/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.put(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def update_resignation_cause_by_id_post(
    id: UUID = Field(..., description="UUID of the resignation cause."),
    query: ResignationCauseModel = Field(ResignationCauseModel(), description="Full query object to update the resignation cause with")
    )->dict:
    """
    Update resignation cause  by id (post).

    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/resignationcauses/{id}"
    payload = query.model_dump(mode="json",by_alias=True,exclude_none=True)
    try:
        response = s.post(
            url,
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    return response.json()

@mcp.tool()
def get_resignation_causes(
    filters: GetResignationCauses = GetResignationCauses()
    )->dict:
    """
    Gets resignation causes optinaly filtered by filter parameters.

    Returns:
        A JSON dict containing the list of resignation causes.
    """
    url = f"{consts.API_ENDPOINT}/resignationcauses"
    try:
        response = s.get(
            url,
            params=filters.model_dump(by_alias=True, exclude_none=True),
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_role_collection_of_user_for_comapany_put(
    query: UpdateRoleCollecitonOfUserForCompany = Field(..., description="List of query objects. company_id and user_id are required for each. All other fields are optional and only sent if explicitly provided."),
    Body: List[RoleModel] = Field(..., description="List of role objects to update id and name are required."),
    )->dict:
    """
    Update the role collection a user have on a company (put).

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/users/{query.user_id}/companies/{query.company_id}/roles"
    params = query.model_dump(by_alias=True, exclude_none=True, exclude={"company_id", "user_id"})
    roles = [
        RoleModel(**role) if isinstance(role, dict) else role
        for role in Body
    ]
    payload = [role.model_dump(mode="json", by_alias=True, exclude_none=True) for role in roles]
    try:
        response = s.put(
            url,
            params=params,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"
    
@mcp.tool()
def update_role_collection_of_user_for_comapany_post(
    query: UpdateRoleCollecitonOfUserForCompany = Field(..., description="List of query objects. company_id and user_id are required for each. All other fields are optional and only sent if explicitly provided."),
    Body: List[RoleModel] = Field(..., description="List of role objects to update id and name are required."),
    )->dict:
    """
    Update the role collection a user have on a company (post).

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/users/{query.user_id}/companies/{query.company_id}/roles"
    params = query.model_dump(by_alias=True, exclude_none=True, exclude={"company_id", "user_id"})
    roles = [
        RoleModel(**role) if isinstance(role, dict) else role
        for role in Body
    ]
    payload = [role.model_dump(mode="json", by_alias=True, exclude_none=True) for role in roles]
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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_all_roles_of_user_for_company(
    query: GetAllRolesOfUserForCompany = Field(..., description="Query object for filtering roles.")
) -> dict:
    """
    Get all roles of a user for a given company.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/users/{query.user_id}/companies/{query.company_id}/roles"
    params=query.model_dump(by_alias=True, exclude_none=True, exclude={"user_id", "company_id"}),

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"
    
@mcp.tool()
def update_role_collection_of_user_for_employee_put(
    query: UpdateRoleCollecitonOfUserForEmployee = Field(..., description="List of query objects. user_id, company_id and employee_id are required for each. All other fields are optional and only sent if explicitly provided."),
    Body: List[RoleModel] = Field(..., description="List of role objects to update id and name are required."),
    )->dict:
    """
    Update the role collection a user have on am employee (put).

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/users/{query.user_id}/companies/{query.company_id}/employees/{query.employee_id}/roles"
    params = query.model_dump(by_alias=True, exclude_none=True, exclude={"company_id", "user_id", "employee_id"})
    roles = [
        RoleModel(**role) if isinstance(role, dict) else role
        for role in Body
    ]
    payload = [role.model_dump(mode="json", by_alias=True, exclude_none=True) for role in roles]
    try:
        response = s.put(
            url,
            params=params,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_role_collection_of_user_for_employee_post(
    query: UpdateRoleCollecitonOfUserForEmployee = Field(..., description="List of query objects. user_id, company_id and employee_id are required for each. All other fields are optional and only sent if explicitly provided."),
    Body: List[RoleModel] = Field(..., description="List of role objects to update id and name are required."),
    )->dict:
    """
    Update the role collection a user have on am employee (post).

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/users/{query.user_id}/companies/{query.company_id}/employees/{query.employee_id}/roles"
    params = query.model_dump(by_alias=True, exclude_none=True, exclude={"company_id", "user_id", "employee_id"})
    roles = [
        RoleModel(**role) if isinstance(role, dict) else role
        for role in Body
    ]
    payload = [role.model_dump(mode="json", by_alias=True, exclude_none=True) for role in roles]
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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_all_roles_of_user_for_employee(
    query: GetAllRolesOfUserForEmployee = Field(..., description="Query object for filtering roles.")
) -> dict:
    """
    Get all roles a user have on a specific employee.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/users/{query.user_id}/companies/{query.company_id}/employees/{query.employee_id}/roles"
    params=query.model_dump(by_alias=True, exclude_none=True, exclude={"user_id", "company_id", "employee_id"}),

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_role_collection_on_account_for_user_put(
    query: UpdateRoleCollectionOnAccountForUser = Field(..., description="List of query objects. user_id, company_id and employee_id are required for each. All other fields are optional and only sent if explicitly provided."),
    Body: List[RoleModel] = Field(..., description="List of role objects to update id and name are required."),
    )->dict:
    """
    Update the role collection on an account for a given user (put).

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/users/{query.user_id}/companies/{query.company_id}/accounts/{query.account_id}/roles"
    params = query.model_dump(by_alias=True, exclude_none=True, exclude={"company_id", "user_id", "account_id"})
    roles = [
        RoleModel(**role) if isinstance(role, dict) else role
        for role in Body
    ]
    payload = [role.model_dump(mode="json", by_alias=True, exclude_none=True) for role in roles]
    try:
        response = s.put(
            url,
            params=params,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_role_collection_on_account_for_user_post(
    query: UpdateRoleCollectionOnAccountForUser = Field(..., description="List of query objects. user_id, company_id and employee_id are required for each. All other fields are optional and only sent if explicitly provided."),
    Body: List[RoleModel] = Field(..., description="List of role objects to update id and name are required."),
    )->dict:
    """
    Update the role collection on an account for a given user (post).

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/users/{query.user_id}/companies/{query.company_id}/accounts/{query.account_id}/roles"
    params = query.model_dump(by_alias=True, exclude_none=True, exclude={"company_id", "user_id", "account_id"})
    roles = [
        RoleModel(**role) if isinstance(role, dict) else role
        for role in Body
    ]
    payload = [role.model_dump(mode="json", by_alias=True, exclude_none=True) for role in roles]
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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_all_roles_of_account(
    query: GetAllRolesOfAccount = Field(..., description="Query object for filtering roles.")
) -> dict:
    """
    Get all roles an account has.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/users/{query.user_id}/companies/{query.company_id}/accounts/{query.account_id}/roles"
    params=query.model_dump(by_alias=True, exclude_none=True, exclude={"user_id", "company_id", "account_id"}),

    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"
    
@mcp.tool()
def get_role_by_id(
    id: UUID = Field(..., description="UUID of the role.")
) -> dict:
    """
    Get role information by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/roles/{id}"
    try:
        response = s.get(
            url,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_roles(
    query: GetRoles = Field(GetRoles(), description="Parameters to filter the search by all feilds optional")
    )->dict:
    """
    Get roles optinaly filtered by filter parameters.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/roles"
    params = query.model_dump(by_alias=True, exclude_none=True)
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_roles_by_user(
    query: GetRolesByUser = Field(..., description="Query object for filtering roles by user. user_id is required. All other fields are optional")
    )->dict:
    """
    Get all roles of a specified user.

    Returns: 
        APi response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/users/{query.user_id}/roles"
    params = query.model_dump(by_alias=True, exclude_none=True, exclude={"user_id"})
    try:
        response = s.get(
            url,
            params=params,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def update_salary_by_id_put(
    salary_id: UUID = Field(..., description="UUID of the salary."),
    salary_data: SalaryModel = Field(..., description="Updated salary data.")
) -> dict:
    """
    Updates a salary by id (put).

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
        return f"API request failed: {e}\n{response.text}"

    return response.json()

@mcp.tool()
def update_salary_by_id_post(
    salary_id: UUID = Field(..., description="UUID of the salary."),
    salary_data: SalaryModel = Field(..., description="Updated salary data.")
) -> dict:
    """
    Updates a salary by id (post).

    Returns:
        Updated salary data as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/salaries/{salary_id}"
    try:
        response = s.post(
            url,
            json=salary_data.model_dump(by_alias=True, exclude_none=True),
            headers={"Content-Type": "application/json"},
            timeout=consts.API_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"

    return response.json()

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
        return f"API request failed: {e}\n{response.text}"
    return response.status_code

@mcp.tool()
def batch_update_salaries_by_employee_id(
    employee_id: UUID = Field(..., description="UUID of the employee."),
    body: List[SalaryModel] = Field(..., description="List of salary objects to update. id is required for each. All other fields are optional and only sent if explicitly provided.")
    ) -> dict:
    """
     Update salaries for an employee.

     Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employees/{employee_id}/salaries"

    salaries = [
        SalaryModel(**salary) if isinstance(salary, dict) else salary
        for salary in body

    ]
    payload = [salary.model_dump(by_alias=True, exclude_none=True, mode="json") for salary in salaries]

    try:
        response = s.put(
            url, 
            params={"employeeId": employee_id},
            json=payload, 
            headers={"Content-Type": "application/json"},
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_salaries(
    query: Optional[GetSalaries] = GetSalaries()
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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def create_salary(
    body: SalaryModel = Field(..., description="Salary object to create. All fields are optional and only sent if explicitly provided.")
    ) -> dict:
    """
     Create a salary for an employee of a given company for a given instance-id. If no instance id is provided, uses default instance-id. 

     Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/salaries"

    payload = body.model_dump(mode="json", by_alias=True, exclude_none=True)
    try:        
        response = s.post(
            url, 
            json=payload, 
            headers={"Content-Type": "application/json"},
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_salary_basis_by_salary_transfer_id(
    salary_transfer_id: UUID = Field(..., description="UUID of the salary transfer."),
    page_params: PageModel = Field(PageModel(), description="Pagination parameters"),
    )->dict:
    """
    Get salarybasis from a salary transfer id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/time/salaryBasis"
    params = {"salaryTransferId": salary_transfer_id,
              "pageIndex": page_params.page_index,
              "pageSize": page_params.page_size
            }

    try:
        response = s.get(
            url, 
            params=params, 
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_salary_basis_by_travel_salary_transfer_id(
    travel_salary_transfer_id: UUID = Field(..., description="UUID of the salary transfer."),
    page_params: Optional[PageModel] = Field(PageModel(), description="Pagination parameters"),
    )->dict:
    """
    Get salarybasis from a travelsalary transfer id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/time/salaryBasis"
    params = {"travelSalaryTransferId": travel_salary_transfer_id,
              "pageIndex": page_params.page_index,
              "pageSize": page_params.page_size
            }

    try:
        response = s.get(
            url, 
            params=params, 
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_salary_statistic_by_employment_period_id(
    employment_period_id: UUID = Field(..., description="UUID of the employment period.")
    )->dict:
    """
    Get a specific employmentperiods salary statistics.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentperiods/{employment_period_id}/salarystatistics"
    try:
        response = s.get(
            url, 
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"
    
@mcp.tool()
def update_salary_statistic_by_employment_period_id_put(
    employment_period_id: UUID = Field(..., description="UUID of the employment period."),
    body: Optional[SalaryStatisticModel] = SalaryStatisticModel()
    )->dict:
    """
    Get a specific employmentperiods salary statistics (put).

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentperiods/{employment_period_id}/salarystatistics"
    payload = body.model_dump(mode="json", by_alias=True, exclude_none=True)
    try:
        response = s.put(
            url, 
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"
    
@mcp.tool()
def update_salary_statistic_by_employment_period_id_post(
    employment_period_id: UUID = Field(..., description="UUID of the employment period."),
    body: Optional[SalaryStatisticModel] = SalaryStatisticModel()
    )->dict:
    """
    Get a specific employmentperiods salary statistics (post).

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employmentperiods/{employment_period_id}/salarystatistics"
    payload = body.model_dump(mode="json", by_alias=True, exclude_none=True)
    try:
        response = s.post(
            url, 
            json=payload,
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_salary_transfer_by_id(
    id: UUID = Field(..., description="UUID of the salary transfer.")
    )->dict:
    """
    Get salary transfer by id.

    Returns:
        API response as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/salaryTransfer/{id}"

    try:
        response = s.post(
            url, 
            timeout=consts.API_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"


#------------------------------------------------------------------------------------------------------------
#
# SALARY TRANSFER NOT YET DONE, MORE TOOLS Here
#
#----------------------------------------------------------------------------------------------------------
@mcp.tool()
def get_schedule_days_by_employee_id(
    query : GetScheduleDaysByEmployee = Field(..., description="Query object for getting schedule days by employee id. employee_id, from_date and to_date are required. All other fields are optional")
    ) -> list:
    """
    Gets schedule days for an employee, optionally filtered by filter parameters.
 
    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/employees/{query.employee_id}/scheduledays"
 
    params = query.model_dump(mode="json", by_alias=True, exclude_none=True, exclude={"employee_id"})
    try:
        response = s.get(url, params=params, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Status: {response.status_code}\n{response.text}"
 
    return response.json()

@mcp.tool()
def get_schedule_days_by_salary_transfer_id(
    query : GetScheduleDaysBySalaryTransfer = Field(..., description="Query object for getting schedule days by salary transfer id. salary_transfer_id is required. All other fields are optional")
    ) -> list:
    """
    Gets schedule days for an employee, optionally filtered by filter parameters.
 
    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/scheduledays" 
 
    params = query.model_dump(by_alias=True, exclude_none=True, exclude={"employee_id"})
    try:
        response = s.get(url, params=params, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Status: {response.status_code}\n{response.text}"
    return response.json()

@mcp.tool()
def get_staff_category_by_id(
    id: UUID = Field(..., description="UUID of the staff category.")
) -> dict:
    """
    Gets schedule days for an employee, optionally filtered by filter parameters.
 
    Returns:
        API response as a JSON dict
    """
    url = f"{consts.API_ENDPOINT}/staffcategories/{id}"

    try:
        response = s.get(url, timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed for staff category {id}: {e}")
    return response.json()




@mcp.tool()
def get_time_report_by_employee(
    query: GetTimeReportByEmployee = Field(..., description="Full query object. employee_id is required. All other fields are optional")
) -> dict:
    """
    Gets a time report for an employee.

    Returns:
        Time report data as a JSON dict.
    """
    url = f"{consts.API_ENDPOINT}/employees/{query.employee_id}/timereport"

    params = query.model_dump(by_alias=True, exclude_none=True, exclude={"employee_id"})
    try:
        response = s.get(url,
            params=params,
            timeout=consts.API_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"API request failed: {e}\n{response.text}"

    return response.json()



@mcp.tool()
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
    print(payload)
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
        return f"API request failed: {e}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

#Works
@mcp.tool()
def get_unions(
    filters: Union = Field(description="Union details for filtering the unions list. All fields are optional and used for filtering the results.")
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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"


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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

@mcp.tool()
def get_users_by_instance(
    filters: GetUsersByInstance = Field(description="User details for filtering the users list. All fields are optional")
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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

#Works
@mcp.tool()
def get_vehicle_types(
    filters: GetVehicleTypes = GetVehicleTypes()
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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"


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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"

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
        return f"API request failed: {e}\n{response.text}"
    if response.headers.get("Content-Type", "").startswith("application/json"):
        return response.json()
    else:
        return f"Status: {response.status_code}\n{response.text}"
    

if __name__ == "__main__":
    mcp.run()