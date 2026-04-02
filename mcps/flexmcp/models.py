from pydantic import BaseModel, Field, field_validator, model_validator
from uuid import UUID
from datetime import date, time, datetime
from typing import Dict, List, Literal, Optional


class TimeRowAccount(BaseModel):
    account_code: Optional[str] = Field(
        None,
        alias="accountCode",
        description=(
            "Account code string. Use together with accountDistributionId to identify "
            "the account, or supply id instead."
        )
    )
    account_distribution_id: Optional[UUID] = Field(
        None,
        alias="accountDistributionId",
        description=(
            "UUID of the account distribution. Use together with accountCode to identify "
            "the account, or supply id instead."
        )
    )
    id: Optional[UUID] = Field(
        None,
        description=(
            "UUID of an existing accounting entry. Use this instead of "
            "accountDistributionId + accountCode when the entry already exists."
        )
    )
 
    model_config = {"populate_by_name": True}

class TimeRow(BaseModel):
    start: Optional[str] = Field(
        None,
        alias="fromTime",
        description=(
            "Start time of the work period (ISO 8601 datetime)."
        )
    )
    end: Optional[str] = Field(
        None,
        alias="tomTime",
        description=(
            "End time of the work period (ISO 8601 datetime)."
        )
    )
    billable: Optional[bool] = Field(
        True,
        description=(
            "Whether the time is billable."
        )
    )
    time_code: Optional[str] = Field(
        None,
        description="Optional time code (e.g. 'WORK', 'OVERTIME')."
    )
    comment: Optional[str] = Field(
        None,
        description="Optional comment for the time entry."
    )
 
    model_config = {"populate_by_name": True}
    
class DayEntry(BaseModel):
    overtime_marking_after: Optional[UUID] = Field(
        None,
        alias="overtimeMarkingAfter"
    )

    overtime_marking_before: Optional[UUID] = Field(
        None,
        alias="overtimeMarkingBefore"
    )

    time_rows: Optional[List[TimeRow]] = Field(
        None,
        alias="timeRows",
        description="List of manual time rows for the day"
    )

    model_config = {"populate_by_name": True}

class AccountLocation(BaseModel):
    latitude: Optional[float] = Field(None, description="Latitude of the account location.")
    longitude: Optional[float] = Field(None, description="Longitude of the account location.")
    location_name: Optional[str] = Field(None, alias="locationName", description="Display name of the location.")
    radius: Optional[int] = Field(None, description="Geofence radius in metres (int32).")
 
    model_config = {"populate_by_name": True}
 
 
class Participant(BaseModel):
    employee_number: Optional[str] = Field(
        None,
        alias="employeeNumber",
        description="Employee number of the participant."
    )
    role: Optional[int] = Field(
        None,
        description="Participant role. 0 = Member, 1 = ProjectManager."
    )
 
    model_config = {"populate_by_name": True}
 
 
class ProjectAccount(BaseModel):
    account_id: UUID = Field(alias="accountId", description="UUID of the account.")
    account_distribution_id: UUID = Field(alias="accountDistributionId", description="UUID of the account distribution.")
    account_code: Optional[str] = Field(None, alias="accountCode", description="Account code string.")
    put_blank: Optional[bool] = Field(None, alias="putBlank", description="Whether to put a blank value for this account.")
    rule_enum: Optional[int] = Field(
        None,
        alias="ruleEnum",
        description="Distribution rule. 0 = CanBeSpecified, 1 = MustBeSpecified, 2 = Locked, -1 = Inheritance."
    )
 
    model_config = {"populate_by_name": True}
 
 
class BillingPriceRowAccount(BaseModel):
    account_id: UUID = Field(alias="accountId", description="UUID of the account.")
    id: UUID = Field(description="UUID of the price row account entry.")
 
    model_config = {"populate_by_name": True}
 
 
class BillingPriceRow(BaseModel):
    id: UUID = Field(description="UUID of the price row.")
    employee_id: Optional[UUID] = Field(None, alias="employeeId", description="UUID of the employee this price row applies to.")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Start date of the price row's validity.")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="End date of the price row's validity.")
    price: Optional[float] = Field(None, description="Base price.")
    price_adjustment: Optional[float] = Field(None, alias="priceAdjustment", description="Fixed price adjustment amount.")
    price_adjustment_percentage: Optional[float] = Field(None, alias="priceAdjustmentPercentage", description="Percentage price adjustment.")
    unit: Optional[int] = Field(
        None,
        description="Billing unit. 0 = Hour, 1 = Day, 2 = HalfDay, 3 = Pcs, 4 = Km, 5 = Mil, 6 = Blank."
    )
    accounts: Optional[list[BillingPriceRowAccount]] = Field(None, description="Accounts associated with this price row.")
 
    model_config = {"populate_by_name": True}
 
 
class AccountBilling(BaseModel):
    price_rows: Optional[list[BillingPriceRow]] = Field(
        None,
        alias="priceRows",
        description="Standard billing price rows."
    )
    price_rows_travel: Optional[list[BillingPriceRow]] = Field(
        None,
        alias="priceRowsTravel",
        description="Travel billing price rows."
    )
 
    model_config = {"populate_by_name": True}
 
 
class ProjectTimeReportControl(BaseModel):
    limit: float = Field(description="The threshold value for the control.")
    summary: int = Field(description="Control summary scope. 0 = Hierarchic, 1 = Individual.")
    type: int = Field(description="Control type. 0 = Warning, 1 = Error.")
 
    model_config = {"populate_by_name": True}
 
 
class Workplace(BaseModel):
    adress: Optional[str] = Field(None, description="Street address. Note: spelled 'adress' in the API.")
    city: Optional[str] = Field(None, description="City.")
    country: Optional[str] = Field(None, description="Country.")
    postal_code: Optional[str] = Field(None, alias="postalCode", description="Postal code.")
    type: Optional[int] = Field(
        None,
        description="Workplace type. 0 = Physical, 1 = Remote, 2 = NotFixed."
    )
 
    model_config = {"populate_by_name": True}
 
 
class ProjectModel(BaseModel):
    code: str = Field(min_length=1, description="Project code. Required.")
    name: str = Field(min_length=1, description="Project name. Required.")
    id: Optional[UUID] = Field(None, description="UUID of the project. Include when updating an existing project.")
    comment: Optional[str] = Field(None, description="Free-text comment.")
    status_enum: Optional[int] = Field(
        None,
        alias="statusEnum",
        description="Project status. 0 = Ongoing, 1 = Frozen, 2 = Ended."
    )
    billing_model_enum: Optional[int] = Field(
        None,
        alias="billingModelEnum",
        description="Billing model. 0 = Ongoing, 1 = Fixed."
    )
    billing_state_enum: Optional[int] = Field(
        None,
        alias="billingStateEnum",
        description="Billing state. 0 = No, 1 = Never, 2 = Yes, 3 = Always."
    )
    travel_billing_state_enum: Optional[int] = Field(
        None,
        alias="travelBillingStateEnum",
        description="Travel billing state. 0 = No, 1 = Never, 2 = Yes, 3 = Always."
    )
    budgeting_time_unit: Optional[int] = Field(
        None,
        alias="budgetingTimeUnit",
        description="Budgeting time unit. 0 = QuarterHour, 1 = HalfHour, 2 = Hour, 3 = Day, 4 = Week, 5 = Month."
    )
    budgeted_hours: Optional[float] = Field(None, alias="budgetedHours", description="Budgeted hours for the project.")
    budgeted_amount: Optional[float] = Field(None, alias="budgetedAmount", description="Budgeted monetary amount for the project.")
    starting_value_reported_time_hours: Optional[float] = Field(
        None,
        alias="startingValueReportedTimeHours",
        description="Starting value for reported time in hours (carries over historical data)."
    )
    start_date: Optional[datetime] = Field(None, alias="startDate", description="Project start date.")
    end_date: Optional[datetime] = Field(None, alias="endDate", description="Project end date.")
    active_from_date: Optional[datetime] = Field(None, alias="activeFromDate", description="Date from which the project is active.")
    active_tom_date: Optional[datetime] = Field(None, alias="activeTomDate", description="Date until which the project is active.")
    tidkod: Optional[str] = Field(None, description="Time code associated with the project.")
    all_employees_are_participants: Optional[bool] = Field(
        None,
        alias="allEmployeesAreParticipants",
        description="If True, all employees are automatically participants."
    )
    inherit_participants: Optional[bool] = Field(None, alias="inheritParticipants", description="Whether participants are inherited from a parent project.")
    inherit_color: Optional[bool] = Field(None, alias="inheritColor", description="Whether the project colour is inherited from a parent project.")
    inherit_competence: Optional[bool] = Field(None, alias="inheritCompetence", description="Whether competence settings are inherited from a parent project.")
    external_comment_must_be_stated_about_billable_time: Optional[bool] = Field(
        None,
        alias="externalCommentMustBeStatedAboutBillableTime",
        description="If True, an external comment is required when reporting billable time."
    )
    participants: Optional[list[Participant]] = Field(None, description="Explicit participants on this project.")
    inherited_participants: Optional[list[Participant]] = Field(
        None,
        alias="inheritedParticipants",
        description="Read-only list of participants inherited from a parent project."
    )
    project_accounts: Optional[list[ProjectAccount]] = Field(
        None,
        alias="projectAccounts",
        description="Account distributions associated with this project."
    )
    account_locations: Optional[list[AccountLocation]] = Field(
        None,
        alias="accountLocations",
        description="Geofenced locations associated with this project."
    )
    billing: Optional[AccountBilling] = Field(None, description="Billing configuration for this project.")
    project_time_report_controls: Optional[list[ProjectTimeReportControl]] = Field(
        None,
        alias="projectTimeReportControls",
        description="Time report controls (warnings/errors) applied to this project."
    )
    work_place: Optional[Workplace] = Field(None, alias="workPlace", description="Workplace associated with this project.")
 
    model_config = {"populate_by_name": True}


class GetSalaryQueryBase(BaseModel):
    instance: Optional[str] = Field(None, description="Domain name.")
    company_id: Optional[UUID] = Field(None, alias="companyId", description="Company ID (UUID).")
    company_number: Optional[int] = Field(None, alias="companyNumber", description="Company number.")
    employee_id: Optional[UUID] = Field(None, alias="employeeId", description="Employee ID (UUID).")
    employment_number: Optional[str] = Field(None, alias="employmentNumber", description="Employment number.")
    page_index: Optional[int] = Field(0, alias="pageIndex", description="Page index. Default value: 0.")
    page_size: Optional[int] = Field(20, alias="pageSize", description="Page size. Default value: 20.")

# For /api/instance/{instance}/salaries: instance required
class GetSalaries(GetSalaryQueryBase):
    instance: str = Field(..., description="Domain name.")

# For /api/instance/{instance}/companies/{companyId}/salaries — instance and companyId required
class GetSalariesByCompany(GetSalaryQueryBase):
    instance: str = Field(..., description="Domain name.")
    company_id: UUID = Field(..., alias="companyId", description="Company ID (UUID).")

#For /api/instance/{instance}/companies/{companyId}/employees/{employeeId}/salaries — instance, companyId and employeeId required
class GetSalariesByCompanyAndEmployee(GetSalaryQueryBase):
    instance: str = Field(..., description="Domain name.")
    company_id: UUID = Field(..., alias="companyId", description="Company ID (UUID).")
    employee_id: UUID = Field(..., alias="employeeId", description="Employee ID (UUID).")

# For /api/instance/{instance}/employees/{employeeId}/salaries — instance and employeeId required
class GetSalariesByEmployee(GetSalaryQueryBase):
    instance: str = Field(..., description="Domain name.")
    employee_id: UUID = Field(..., alias="employeeId", description="Employee ID (UUID).")

#For /api/salaries — no parameters required
class GetAllSalaries(GetSalaryQueryBase):
    pass

#For /api/employees/{employeeId}/salaries — employeeId required
class UpdateOrCreateSalaries(BaseModel):
    comment: Optional[str] = Field(None, description="Comment. Nullable.")
    company_id: UUID = Field(..., alias="companyId", description="Company ID (UUID).")
    employee_id: UUID = Field(..., alias="employeeId", description="Employee ID (UUID).")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Start date. Nullable.")
    full_time_salary: Optional[float] = Field(None, alias="fullTimeSalary", description="Full time salary.")
    id: Optional[UUID] = Field(None, description="Salary ID (UUID).")
    instance_id: UUID = Field(..., alias="instanceId", description="Instance ID (UUID).")
    is_historical_salary: Optional[bool] = Field(None, alias="isHistoricalSalary", description="Whether this is a historical salary.")
    salary_type: Optional[int] = Field(None, alias="salaryType", description="0 = Monthly, 1 = Hourly, 2 = Yearly.")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="End date. Nullable.")

class StampingAccountModel(BaseModel):
    accountCode: str = Field(..., min_length=1, description="Account code string.")
    accountDistributionId: UUID = Field(..., description="UUID of the account distribution.")

class Union(BaseModel):
    instance: Optional[str] = Field(None, description="Domain name.")
    company_id: Optional[UUID] = Field(None, description="Company id.")
    company_number: Optional[int] = Field(None, description="Company number.")
    pageIndex: Optional[int] = Field(0, description="Page index for search. Begins at 0.")
    pageSize: Optional[int] = Field(20, description="Number of entries per page.")

class GetUsersQueryBase(BaseModel):
    instans: Optional[str] = Field(None, description="Domain name.")
    username: Optional[str] = Field(None, description="User name.")
    extern_ref: Optional[str] = Field(None, description="External reference.")
    user_type: Optional[int] = Field(None, description="User type") #Vilken int är vad?
    active: Optional[bool] = Field(None, description="Are the useres active.")
    logon_since: Optional[datetime] = Field(None, description="Did the user log in since.")
    no_logon_since: Optional[datetime] = Field(None, description="Did the user not log in since.")
    page_index: Optional[int] = Field(0, description="Page index for search. Begins at 0.")
    page_size: Optional[int] = Field(20, description="Number of entries per page")

class GetUsers(GetUsersQueryBase):
    pass

class GetUsersByInstance(GetUsersQueryBase):
    instance: str = Field(..., description="Domain name.")

