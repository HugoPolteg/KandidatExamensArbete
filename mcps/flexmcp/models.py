from dotenv import load_dotenv
import os
load_dotenv()
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, field_serializer
from uuid import UUID
from datetime import date, time, datetime
from typing import Dict, List, Literal, Optional

INSTANCE = os.getenv("INSTANCE")
DOMAIN = os.getenv("DOMAIN")

class PageModel(BaseModel):
    page_index: Optional[int] = Field(0, alias="pageIndex", description="Page index dafault value 0."),
    page_size: Optional[int] = Field(20, alias="pageSize", description="Page size dafault value 20.")

class AbsenceStatusModel(BaseModel):
    absence_application_id: UUID = Field(..., alias="absenceApplicationId", description="UUID of the absence application.")
    id: UUID = Field(..., description="UUID of this status record.")
    message: Optional[str] = Field(None, description="Message from the approver regarding the absence application.")
    status: int = Field(..., description="Status of the absence application.")
    time_stamp: datetime = Field(..., alias="timeStamp", description="Timestamp of the absence status.")
    user_id: UUID = Field(..., alias="userId", description="UUID of the user who made the status update.")
    user_signature: Optional[str] = Field(None, alias="userSignature", description="Signature of the user who made the status update.")

class ImportAbsenceApplicationModelAPIBase(BaseModel):
    absence_type_id: UUID = Field(..., alias="absenceTypeId", description="UUID of the absence type.")
    child_id: Optional[UUID] = Field(None, alias="childId", description="UUID of the child for which the absence application is made.")
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    current_status: Optional[AbsenceStatusModel] = Field(None, alias="currentStatus", description="Current status of the absence application if it exists.")
    employment_number: str = Field(..., min_length=1,alias="employmentNumber", description="Employment number of the applicant.")
    from_date: date = Field(..., alias="fromDate", description="Start date of the absence.")
    from_time: Optional[time] = Field(None, alias="fromTime", description="Start time of the absence.")
    hours: Optional[float] = Field(None, description="Number of hours for the absence.")
    id: UUID=Field(..., description="UUID of the absence application.")
    message: Optional[str] = Field(None, description="Message from the applicant regarding the absence application.")
    part_time_percentage: Optional[float] = Field(None, alias="partTimePercentage", description="Part-time percentage for the absence application.")
    status: Optional[AbsenceStatusModel] = Field(None, description="Status to which the application whiches to be set")
    to_date: Optional[date] = Field(..., alias="toDate", description="End date of the absence.")
    to_time: Optional[time] = Field(None, alias="toTime", description="End time of the absence.")

class AccountModel(BaseModel):
    account_locations: Optional[List[AccountLocationModel]] = Field(None,alias="accountLocations",description="A list of account locations")
    active_from_date: Optional[datetime] = Field(None,alias="activeFromDate",description="Account active from date")
    active_to_date: Optional[datetime] = Field(None,alias="activeTomDate",description="Account active to date")
    billing: Optional[AccountBillingModel]
    billing_state_enum: Optional[int] = Field(alias="billingStateEnum",description="Billing state: 0 = No, 1 = Never, 2 = Yes, 3 = Always")
    budgeting_time_unit: Optional[int] = Field(alias="budgetingTimeUnit", description="Budgeting time unit. 0 = QuarterHour, 1 = HalfHour, 2 = Hour, 3 = Day, 4 = Week, 5 = Month.")
    code: str = Field(min_length=1, description="Unique account code")
    external_comment_must_be_stated_about_billable_time: Optional[bool] = Field(None, alias="externalCommentMustBeStatedAboutBillableTime", description="Whether an external comment must be stated about billable time.")
    id: Optional[UUID] = Field(None, description="UUID of the account.")
    name: str = Field(..., description="Account name. Minimum length: 1.")
    travel_billing_state_enum: Optional[int] = Field(None, alias="travelBillingStateEnum", description="Travel billing state. 0 = No, 1 = Never, 2 = Yes, 3 = Always.")
    work_place: Optional[WorkplaceModel] = Field(None, alias="workPlace", description="Workplace details associated with the account.")

class AccountLocationModel(BaseModel):
    latitude: Optional[float] = Field(None,description="Latitude of the location")
    location_name: Optional[str] = Field(None,alias="locationName",description="Name of the location")
    longitude: Optional[float] = Field(None,description="Longitude of the locaiton")
    radius: Optional[int] = Field(None,description="Radius of the location")

class AccountBillingModel(BaseModel):
    price_rows: Optional[list[AccountBillingPriceRowModel]] = Field(None, alias="priceRows", description="List of standard billing price rows. Nullable.")
    price_row_travel: Optional[list[AccountBillingPriceRowModel]] = Field(None, alias="priceRowTravel", description="List of travel billing price rows. Nullable.")

class AccountBillingPriceRowModel(BaseModel):
    accounts: Optional[list[AccountBillingPriceRowAccountModel]] = Field(None, description="List of accounts associated with this price row.")
    employee_id: Optional[UUID] = Field(None, alias="employeeId", description="UUID of the employee associated with this price row. Nullable.")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Start date of the price row validity period. Nullable.")
    id: Optional[UUID] = Field(None, description="UUID of the billing price row record.")
    price: Optional[float] = Field(None, description="Price value. Nullable.")
    price_adjustment: Optional[float] = Field(None, alias="priceAdjustment", description="Price adjustment value. Nullable.")
    price_adjustment_percentage: Optional[float] = Field(None, alias="priceAdjustmentPercentage", description="Price adjustment percentage. Nullable.")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="End date of the price row validity period. Nullable.")
    unit: Optional[int] = Field(None, description="Billing row unit. 0 = Hour, 1 = Row, 2 = HalfDay, 3 = Pos, 4 = Km, 5 = Mil, 6 = Blank.")

class AccountBillingPriceRowAccountModel(BaseModel):
    account_id: Optional[UUID] = Field(None, alias="accountId", description="UUID of the account.")
    id: Optional[UUID] = Field(None, description="UUID of the price row account entry.")

class WorkplaceModel(BaseModel):
    adress: Optional[str] = Field(None, description="Adress of the workplace")
    city: Optional[str] = Field(None,description="City of the workspace")
    country: Optional[str] = Field(None,description="Country of the workspace")
    postal_code: Optional[str] = Field(None,alias="postalCode",description="Postal code of the workplace")
    type: Optional[int] = Field(description="Type of workspace: 0 = Physical, 1 = Remote, 2 = NotFixed")

class GetAccountByAccountDistributionId(BaseModel):
    code: Optional[str] = Field(None, description="Account code")
    page_index: Optional[int] = Field(0, alias="pageIndex", description="Page index dafault value 0."),
    page_size: Optional[int] = Field(20, alias="pageSize", description="Page size dafault value 20.")
    modified_since: Optional[datetime] = Field(alias="modifiedSince",description="Get accounts that have been created or modified from this date and time.")

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

class GetReportedHoursModel(BaseModel):
    account_distribution_ids: Optional[list[str]] = Field(None,alias="accountDistributionIds",description="A list of account distribution ids")
    from_date_time: Optional[datetime] = Field(None,alias="fromDateTime",description="Get hours reported after this time")
    hide_projects_with_no_reported_hours: Optional[bool] = Field(alias="hideProjectsWithNoReportedHours",description="Whether to hide project with no repoted hours")
    include_allowances: Optional[bool] = Field(alias="includeAllowances",description="Whether to include Employements")
    include_open_timerows: Optional[bool] = Field(alias="includeOpenTimerows",description="Whether to include open timerows")
    include_undefined_timecodes: Optional[bool] = Field(alias="includeUndefinedTimeCodes",description="Whether to include undefined time codes")
    max_hours_open_time_row: Optional[int] = Field(None, alias="maxHoursOpenTimeRow", description="The maximum amount of hours selected timerows should be have been open for")
    time_group_id: Optional[UUID] = Field(None, alias="timeGroupId",description="Id of the timegroup")
    to_date_time: Optional[datetime] = Field(None,alias="TomDateTime",description="Get hours reported uo to this time")   

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
    instance: Optional[str] = Field(INSTANCE, description="Domain name.")
    company_id: Optional[UUID] = Field(None, alias="companyId", description="Company ID (UUID).")
    company_number: Optional[int] = Field(None, alias="companyNumber", description="Company number.")
    employee_id: Optional[UUID] = Field(None, alias="employeeId", description="Employee ID (UUID).")
    employment_number: Optional[str] = Field(None, alias="employmentNumber", description="Employment number.")
    page_index: Optional[int] = Field(0, alias="pageIndex", description="Page index. Default value: 0.")
    page_size: Optional[int] = Field(20, alias="pageSize", description="Page size. Default value: 20.")
    model_config = ConfigDict(populate_by_name=True)

# For Get/api/instance/{instance}/salaries: instance required
class GetSalaries(GetSalaryQueryBase):
    pass

# For Get/api/instance/{instance}/companies/{companyId}/salaries — instance and companyId required
class GetSalariesByCompany(GetSalaryQueryBase):
    company_id: UUID = Field(..., alias="companyId", description="Company ID (UUID).")

#For Get/api/instance/{instance}/companies/{companyId}/employees/{employeeId}/salaries — instance, companyId and employeeId required
class GetSalariesByCompanyAndEmployee(GetSalaryQueryBase):
    company_id: UUID = Field(..., alias="companyId", description="Company ID (UUID).")
    employee_id: UUID = Field(..., alias="employeeId", description="Employee ID (UUID).")

# For Get/api/employees/{employeeId}/salaries —  employeeId required
class GetSalariesByEmployee(GetSalaryQueryBase):
    instance: Optional[str] = Field(None, description="Domain name.")
    employee_id: UUID = Field(..., alias="employeeId", description="Employee ID (UUID).")

#For Get/api/salaries — no parameters required
class GetAllSalaries(GetSalaryQueryBase):
    instance: Optional[str] = Field(None, description="Domain name.")



class Salary(BaseModel):
    comment: Optional[str] = Field(None, description="Comment. Nullable.")
    company_id: UUID = Field(None, alias="companyId", description="Company ID (UUID).")
    employee_id: UUID = Field(None, alias="employeeId", description="Employee ID (UUID).")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Start date. Nullable.")
    full_time_salary: Optional[float] = Field(None, alias="fullTimeSalary", description="Full time salary per period defined in salary_type (Monthly, hourly or yearly)")
    id: Optional[UUID] = Field(None, description="Salary ID (UUID).")
    instance_id: UUID = Field(INSTANCE, alias="instanceId", description="Instance ID (UUID).")
    is_historical_salary: Optional[bool] = Field(None, alias="isHistoricalSalary", description="Whether this is a historical salary.")
    salary_type: Optional[int] = Field(None, alias="salaryType", description="0 = Monthly, 1 = Hourly, 2 = Yearly.")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="End date. Nullable.")
    model_config = ConfigDict(populate_by_name=True)

    @field_serializer("from_date", "to_date")
    def serialize_datetime(self, value: Optional[datetime]):
        if value is None:
            return value
        return value.strftime("%Y-%m-%dT%H:%M:%S")

#For PUT/api/employees/{employeeId}/salaries — employeeId required
class UpdateOrCreateSalaries(Salary):
    company_id: UUID = Field(..., alias="companyId", description="Company ID (UUID).")
    employee_id: UUID = Field(..., alias="employeeId", description="Employee ID (UUID).")


class StampingAccountModel(BaseModel):
    accountCode: str = Field(..., min_length=1, description="Account code string.")
    accountDistributionId: UUID = Field(..., description="UUID of the account distribution.")
    model_config = ConfigDict(populate_by_name=True)

class Union(BaseModel):
    instance: Optional[str] = Field(None, description="Domain name.")
    company_id: Optional[UUID] = Field(None, description="Company id.")
    company_number: Optional[int] = Field(None, description="Company number.")
    page_index: Optional[int] = Field(0, description="Page index for search. Begins at 0.")
    page_size: Optional[int] = Field(20, description="Number of entries per page.")
    model_config = ConfigDict(populate_by_name=True)

class ListCompaniesInput(BaseModel):
    instance: Optional[str] = Field(
        default=DOMAIN,
        description="Domain name. If not provided, defaults to the default-domain instance."
    )
    page_index: Optional[int] = Field(
        default=0,
        description="Page index for search. Begins at 0."
    )
    page_size: Optional[int] = Field(
        default=20,
        description="Number of entries per page."
    )
    model_config = ConfigDict(populate_by_name=True)

class GetUsers(BaseModel):
    instance: Optional[str] = Field(INSTANCE, description="Domain name.")
    username: Optional[str] = Field(None, description="User name.")
    extern_ref: Optional[str] = Field(None, description="External reference.")
    user_type: Optional[int] = Field(None, description="User type: 1 = System, 2 = Instance") 
    active: Optional[bool] = Field(None, description="Are the useres active.")
    logon_since: Optional[datetime] = Field(None, description="Did the user log in since.")
    no_logon_since: Optional[datetime] = Field(None, description="Did the user not log in since.")
    page_index: Optional[int] = Field(0, description="Page index for search. Begins at 0.")
    page_size: Optional[int] = Field(20, description="Number of entries per page")
    model_config = ConfigDict(populate_by_name=True)

class GetUsersByInstance(GetUsers):
    instance: str = Field(INSTANCE, description="Domain name.")

class GetVehicleType(BaseModel):
    company_id: Optional[UUID] = Field(None, alias="companyId", description="Company ID (UUID).")
    vechile_type: Optional[int] = Field(None, alias="vehicleType", description="Vehicle type string to search for: 0 = Private, 1 = Business")
    comsumption_unit: Optional[int] = Field(None, alias="consumptionUnit", description="Consumption unit: 0 = LPer100Km, 1 = KWhPer100Km")
    page_index: Optional[int] = Field(0, alias="pageIndex", description="Page index for search. Begins at 0.")
    page_size: Optional[int] = Field(20, alias="pageSize", description="Number of entries per page")
    model_config = ConfigDict(populate_by_name=True)

class GetVehicleTypeByCompanyId(GetVehicleType):
    company_id: UUID = Field(..., alias="companyId", description="Company ID (UUID).")

class VehicleTypeRequestModel(BaseModel):
    average_fuel_price_from_month: Optional[int] = Field(None, alias="fromMonth", description="Average fuel price from month (1-12).")
    average_fuel_price_from_year: Optional[int] = Field(None, alias="fromYear", description="Average fuel price from year (e.g. 2023).")
    average_fuel_price_id: Optional[UUID] = Field(None, alias="id", description="UUID of the average fuel price to use for the vehicle type.")
    average_fuel_price: Optional[float] = Field(None, alias="price", description="Average fuel price to use for the vehicle type.")
    average_fuel_price_to_month: Optional[int] = Field(None, alias="toMonth", description="Average fuel price to month (1-12).")
    average_fuel_price_to_year: Optional[int] = Field(None, alias="toYear", description="Average fuel price to year (e.g. 2025).")
    company_id: Optional[UUID] = Field(..., alias="companyId", description="Company ID (UUID).")
    consumption_unit_type: Optional[int] = Field(None, alias="consumptionUnit", description="Consumption unit: 0 = LPer100Km, 1 = KWhPer100Km")
    default_private_vehicle: Optional[bool] = Field(None, alias="defaultPrivateVehicle", description="Whether this is the default private vehicle.")
    fuel_benefit_20_percent_paycode_id: Optional[UUID] = Field(None, alias="fuelBenefit20PercentPaycodeId", description=r"UUID of the pay code to use for the 20% fuel benefit when this vehicle type is used.")
    fuel_benefit_paycode_id: Optional[UUID] = Field(None, alias="fuelBenefitPaycodeId", description="UUID of the pay code to use for the fuel benefit when this vehicle type is used.")
    id: Optional[UUID] = Field(None, description="UUID of the vehicle type.")
    mileage_limit_template_id: Optional[UUID] = Field(None, alias="mileageLimitTemplateId", description="UUID of the mileage limit template to use for this vehicle type.")
    name: Optional[str] = Field(None, description="Name of the vehicle type.")
    taxed_allowance_amount: Optional[float] = Field(None, alias="taxedAllowanceAmount", description="Taxed allowance amount for this vehicle type.")
    taxed_allowance_paycode_id: Optional[UUID] = Field(None, alias="taxedAllowancePaycodeId", description="UUID of the pay code to use for the taxed allowance when this vehicle type is used.")
    tax_free_allowance_amount: Optional[float] = Field(None, alias="taxFreeAllowanceAmount", description="Tax free allowance amount for this vehicle type.")
    tax_free_allowance_paycode_id: Optional[UUID] = Field(None, alias="taxFreeAllowancePaycodeId", description="UUID of the pay code to use for the tax free allowance when this vehicle type is used.")
    type: Optional[int] = Field(None, alias="vehicleType", description="Vehicle type: 0 = Private, 1 = Business")
    use_with_allowances: Optional[bool] = Field(None, alias="useWithAllowances", description="Whether this vehicle type can be used together with allowances.")
    use_with_benefit: Optional[bool] = Field(None, alias="useWithBenefit", description="Whether this vehicle type can be used together with benefits.")
    model_config = ConfigDict(populate_by_name=True)

class GetTravelClaims(BaseModel):
    instance: Optional[str] = Field(None, description="Domain name.")
    company_number: Optional[int] = Field(None, alias="companyNumber", description="Company number.")
    employment_number: Optional[str] = Field(None, alias="employmentNumber", description="Employment number.")
    payment_from_date: Optional[datetime] = Field(None, alias="paymentFromDate", description="Payment from date.")
    payment_to_date: Optional[datetime] = Field(None, alias="paymentToDate", description="Payment to date.")
    audit_from_date: Optional[datetime] = Field(None, alias="auditFromDate", description="Audit from date. Will check all audit levels if publicTravelClaimAuditLevelId is not specified.")
    audit_to_date: Optional[datetime] = Field(None, alias="auditToDate", description="Audit to date. Will check all audit levels if publicTravelClaimAuditLevelId is not specified.")
    public_travel_claim_audit_level_id: Optional[UUID] = Field(None, alias="publicTravelClaimAuditLevelId", description="UUID of the public travel claim audit level.  Must be used in combination with atleast one of auditFromDate/auditToDate. If not specified, will check all audit levels.")
    billing_release_from_date: Optional[datetime] = Field(None, alias="billingReleaseFromDate", description="Get travel claims by billing release from date-time.")
    billing_release_to_date: Optional[datetime] = Field(None, alias="billingReleaseToDate", description="Get travel claims by billing release to date-time.")
    page_index: Optional[int] = Field(0, alias="pageIndex", description="Page index. Default value: 0.")
    page_size: Optional[int] = Field(20, alias="pageSize", description="Page size. Default value: 20.")
    model_config = ConfigDict(populate_by_name=True)



