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
    status: int = Field(..., description="Status of the absence application.") #Hittar inte vilka int som motsvarar vad
    time_stamp: datetime = Field(..., alias="timeStamp", description="Timestamp of the absence status.")
    user_id: UUID = Field(..., alias="userId", description="UUID of the user who made the status update.")
    user_signature: Optional[str] = Field(None, alias="userSignature", description="Signature of the user who made the status update.")

class WorkplaceModel(BaseModel):
    adress: Optional[str] = Field(None, description="Adress of the workplace")
    city: Optional[str] = Field(None,description="City of the workspace")
    country: Optional[str] = Field(None,description="Country of the workspace")
    postal_code: Optional[str] = Field(None,alias="postalCode",description="Postal code of the workplace")
    type: Optional[int] = Field(None, description="Type of workspace: 0 = Physical, 1 = Remote, 2 = NotFixed")

class CreateAbsenceApplicationQuery(BaseModel):
    apply_approval: Optional[bool] = Field(False, alias="applyApproval", description="Decides whether the absence application has automatic approval to the highest level. Default value false.")
    is_part_time_absence: Optional[bool] = Field(False, alias="isPartTimeAbsence", description="Decides whether the absence application is part time absence. Default false.")

class ImportAbsenceApplicationModelAPIBase(BaseModel):
    absence_type_id: UUID = Field(..., alias="absenceTypeId", description="UUID of the absence type.")
    child_id: Optional[UUID] = Field(None, alias="childId", description="UUID of the child for which the absence application is made.")
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    current_status: Optional[AbsenceStatusModel] = Field(None, alias="currentStatus", description="Current status of the absence application if it exists.")
    employment_number: str = Field(..., min_length=1,alias="employmentNumber", description="Employment number of the applicant.")
    from_date: datetime = Field(..., alias="fromDate", description="Start date of the absence.")
    from_time: Optional[time] = Field(None, alias="fromTime", description="Start time of the absence.")
    hours: Optional[float] = Field(None, description="Number of hours for the absence.")
    id: UUID=Field(..., description="UUID of the absence application that information is imported from.")
    message: Optional[str] = Field(None, description="Message from the applicant regarding the absence application.")
    part_time_percentage: Optional[float] = Field(None, alias="partTimePercentage", description="Part-time percentage for the absence application.")
    status: Optional[AbsenceStatusModel] = Field(None, description="Status to which the application whiches to be set")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="End date of the absence.")
    to_time: Optional[time] = Field(None, alias="toTime", description="End time of the absence.")
    model_config = {"populate_by_name": True}
    @field_serializer("from_date", "to_date")
    def serialize_datetime(self, value: datetime):
        return value.replace(tzinfo=None).isoformat(timespec="milliseconds") + "Z"

class AccountLocationModel(BaseModel):
    latitude: Optional[float] = Field(None, description="Latitude of the account location.")
    longitude: Optional[float] = Field(None, description="Longitude of the account location.")
    location_name: Optional[str] = Field(None, alias="locationName", description="Display name of the location.")
    radius: Optional[int] = Field(None, description="Geofence radius in metres (int32).")
 
    model_config = {"populate_by_name": True}


class AccountBillingPriceRowAccountModel(BaseModel):
    account_id: Optional[UUID] = Field(None, alias="accountId", description="UUID of the account.")
    id: Optional[UUID] = Field(None, description="UUID of the price row account entry.")

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


class AccountBillingModel(BaseModel):
    price_rows: Optional[list[AccountBillingPriceRowModel]] = Field(None, alias="priceRows", description="List of standard billing price rows. Nullable.")
    price_row_travel: Optional[list[AccountBillingPriceRowModel]] = Field(None, alias="priceRowTravel", description="List of travel billing price rows. Nullable.")


class GetAccountByAccountDistributionId(BaseModel):
    code: Optional[str] = Field(None, description="Account code")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    modified_since: Optional[datetime] = Field(None, alias="modifiedSince",description="Get accounts that have been created or modified from this date and time.")

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
    hide_projects_with_no_reported_hours: Optional[bool] = Field(None, alias="hideProjectsWithNoReportedHours",description="Whether to hide project with no repoted hours")
    include_allowances: Optional[bool] = Field(None, alias="includeAllowances",description="Whether to include Employements")
    include_open_timerows: Optional[bool] = Field(None,alias="includeOpenTimerows",description="Whether to include open timerows")
    include_undefined_timecodes: Optional[bool] = Field(None,alias="includeUndefinedTimeCodes",description="Whether to include undefined time codes")
    max_hours_open_time_row: Optional[int] = Field(None, alias="maxHoursOpenTimeRow", description="The maximum amount of hours selected timerows should be have been open for")
    time_group_id: Optional[UUID] = Field(None, alias="timeGroupId",description="Id of the timegroup")
    to_date_time: Optional[datetime] = Field(None,alias="TomDateTime",description="Get hours reported uo to this time")

class GetAccountBudgetByAccountId(BaseModel):
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="From date. Get account budget from date.")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="From date. Get account budget from date.")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")

class AccountBudgetModel(BaseModel):
    actual_sales: float = Field(...,alias="actualSales",description="The observed sales")
    budgeted_cost: float = Field(...,alias="budgetedCost",description="The budgeted costs")
    budgeted_hours: float = Field(...,alias="budgetedHours",description="The budgeted hours")
    budgeted_sales: float = Field(...,alias="budgetedSales",description="The budgeted sales")
    date_time: str = Field(...,min_length=1,alias="dateTime",description="Budget period identifier as a string.")
    id: UUID = Field(None, description="UUID of the Account budget")

class AccountModel(BaseModel):
    account_locations: Optional[List[AccountLocationModel]] = Field(None, alias="accountLocations", description="A list of account locations")
    active_from_date: Optional[datetime] = Field(None,alias="activeFromDate",description="Account active from date")
    active_to_date: Optional[datetime] = Field(None,alias="activeTomDate",description="Account active to date")
    billing: Optional[AccountBillingModel] = Field(None,description="billing")
    billing_state_enum: Optional[int] = Field(None,alias="billingStateEnum",description="Billing state: 0 = No, 1 = Never, 2 = Yes, 3 = Always")
    budgeting_time_unit: Optional[int] = Field(None,alias="budgetingTimeUnit", description="Budgeting time unit. 0 = QuarterHour, 1 = HalfHour, 2 = Hour, 3 = Day, 4 = Week, 5 = Month.")
    code: str = Field(None, min_length=1, description="Unique account code")
    external_comment_must_be_stated_about_billable_time: Optional[bool] = Field(None, alias="externalCommentMustBeStatedAboutBillableTime", description="Whether an external comment must be stated about billable time.")
    id: Optional[UUID] = Field(None, description="UUID of the account.")
    name: str = Field(..., description="Account name. Minimum length: 1.")
    travel_billing_state_enum: Optional[int] = Field(None, alias="travelBillingStateEnum", description="Travel billing state. 0 = No, 1 = Never, 2 = Yes, 3 = Always.")
    work_place: Optional[WorkplaceModel] = Field(None, alias="workPlace", description="Workplace details associated with the account.")



class AccountCombinationAccountModel(BaseModel):
    account_distribution: UUID = Field(...,alias="accountDistribution",description="UUID of the account distribution")
    account_selection: str = Field(...,min_length=1,alias="accountSelection",description="Code identifying the selected account within the distribution.")

class AccountCombinationModel(BaseModel):
    account_combination_accounts: Optional[List[AccountCombinationAccountModel]] = Field(None,alias="accountCombinationAccounts",description="List of combination accounts")
    combination_rule: int = Field(...,alias="combinationRule",description="Whether or not to allow posting combination: 1 = Allow, -1 = Do not Allow")
    company_id: UUID = Field(...,alias="companyId",description="UUID of the company")

class GetAccountDistribution(BaseModel):
    company: str = Field(...,description="Company number"),
    instance: str = Field(INSTANCE,description="Domain name"),
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")

class AccountDistributionPartApprovalPermissionModel(BaseModel):
    account_distribution_id: UUID = Field(...,alias="accountDistributionId",description="UUID of the account distribution")
    id: UUID = Field(...,description="Part approval Permisson id")
    premission_to_account_without_row_or_account: bool = Field(...,alias="premissionToAccountWithoutRowOrAccount",description="Whether the user has permission to approve account distributions without a specified row or account.")
    premission_to_all_accounts: bool = Field(..., alias="premissionToAllAccounts", description="Whether the user has permission to approve all accounts.")
    user_id: UUID = Field(..., alias="userId", description="UUID of the user this permission applies to.")

class GetCompanyAccountApprovalPermississons(BaseModel):
    instance: Optional[str] = Field(None,description="instance")
    companynumber: Optional[int] = Field(None,description="companynumber")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")
    user_id: Optional[UUID] = Field(None,alias="userId",description="UUID of the user")

class GetAccumulators(BaseModel):
    company_id: Optional[UUID] = Field(None,alias="companyId",description="UUID of the company")
    accumulator_type: Optional[int] = Field(None,alias="accumulatorType",description="Type of the accumulator:0 = None, 1 = Gross, 2 = Benefit, 3 = Tax, 4 = Allowance, 5 = Deduction, 6 = DebtGross, 7 = DebtNet")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")

class GetAllowanceRuleSet(BaseModel):
    company_id: Optional[UUID] = Field(None,alias="companyId",description="UUID of the company")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")

class GetAuditedTimeReportsByCompany(BaseModel):
    salary_transfer_id: Optional[UUID] = Field(None,alias="salartTransferId",description="Get time reports that have been sent to salary using the salary tranfer id")
    from_date: Optional[datetime] = Field(None,alias="fromDate",description="Time reports reported after this date")
    to_date: Optional[datetime] = Field(None,alias="fromDate", description="Time reports reported before this date")
    approved_from_date: Optional[datetime] = Field(None,alias="approvedFromDate",description="Get time reports that have been audited after this date")
    approved_to_date: Optional[datetime]  = Field(None,alias="approvedToDate",description="Get time reports that have been audited before this date")
    audit_level_id: Optional[str] = Field(None,alias="auditLevelId",description="Get time reports that have been audited with this audit level id. If empty all audit levels will be selected")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")

class GetTimeReportByEmployee(BaseModel):
    employee_id: UUID = Field(..., alias="employeeId", description="employee id")
    date: Optional[datetime] = Field(None, description="Time reports reported after this date")
    generated: Optional[bool] = Field(True, description="Include generated time rows")
    model_config = ConfigDict(populate_by_name=True)

class GetBackGroundTasks(BaseModel):
    worker_state: Optional[int] = Field(None,alias="workerState", description="Worker state of the background task: 0 = Enqueued, 1 = Scheduled, 2 = Processing, 3 = Succeeded, 4 = Failed, 5 = Deleted, 6 = Awaiting")
    worker_function: Optional[int] = Field(None,alias="workerFunction", description="Function of the worker: 0 = None, 1 = Exempelfunktion, 2 = Dygnsrutin, 3 = Mailer, 4 = ValutakursImport, 5 = PaminnelseTidrapport, 6 = Paminnelse, 7 = RensaReserakningar, 8 = RensaTidrapporter, 9 = UtrikesTraktamenteImport, 10 = CreateForetag, 11 = ResaLoneoverforing, 12 = TidLoneoverforing, 13 = CreateForetagsinstallningarFil, 14 = Importmallsimport, 15 = DeleteForetag, 16 = DeleteKundinstans, 17 = DeleteForetagsinstallningarFil, 18 = OverwriteForetag, 19 = Lonekorning, 20 = FrislappTillFakturering, 21 = JeevesQueueSender, 22 = RollbackFrislappTillFakturering, 23 = FirstCardFileRetreivalAndKontokortImport, 24 = EurocardKontokortImport, 25 = Meddelanden, 26 = SkattetabellImport, 27 = Export, 28 = SchemalagdKorning, 29 = UppdateraAckumulator, 30 = ExportAnstalld, 31 = RefreshTidrapporter, 32 = Lonerevision, 33 = CalculateLonekorningAnstallning, 34 = UpdateDatabase, 35 = FortnoxKonteringsimport, 36 = DanskeBankKontokortImport, 37 = FortnoxBokforingsoverforing, 38 = TidDelbifall, 39 = RecalculateReserakningar, 40 = KopieraSchema, 41 = FlexOnlineSystemInformationSender, 42 = AutoBemanning, 43 = Felmeddelandeutskick, 44 = LonBokforingsunderlag, 45 = Kontrolluppgifter, 46 = UpdateNarvarotablaData, 47 = InitiatePayroll, 48 = Semesterarsskifte, 49 = SenAnkomstPaminnelse, 50 = UtbetalningAvLon, 51 = AnonymiseringPersonuppgifter, 52 = Semesterskuld, 53 = PassforfraganAnswer, 54 = Formel, 55 = TidregistreringAvvikelseinstallning, 56 = Tidregistreringsinstallning, 57 = TidregistreringStamplinginstallning, 58 = TidrapporteringColumnLayoutinstallning, 59 = TidregistreringAvvikelsetyperInstallning, 60 = Agi, 61 = Kontokortsfil, 62 = KvittoScanning, 63 = SprakFilerFromFlexOnline, 64 = StandardvardenForDynamiskOversattningFromFlexOnline, 65 = StandardvardenForDynamiskOversattningTillFlexOnline, 66 = FlexKontokort, 67 = PensionOchForsakring, 68 = LonerevisionClearInactiveRowLocks, 69 = LicensFromFlexOnline, 70 = XledgerIntegration, 71 = Onboarding, 72 = UteblivenStamplingPaminnelse, 73 = UteblivenStamplingPaminnelseScheduler, 74 = Arbetsgivarintyg, 75 = FragaOmSkatteavdrag, 76 = KonjunkturstatistikKLP, 77 = KopieraForetag, 79 = OfflineStamplingar, 80 = KonjunkturstatistikKSju, 81 = KonjunkturstatistikKSP, 82 = LonestrukturstatistikSLP, 83 = CalculateTidrapportdagDataWorkerService, 84 = ResetTidrapportdagDataWorkerService, 85 = Retrolon, 86 = KomprimeraBilagor, 87 = VerifiedSync, 88 = AnstallningSemesterinstallning, 89 = AnstallningSemesterarIngaendeVarde, 90 = AnstallningSemesterarSemestersaldo, 91 = LonekorningAnstallningSemesterarSemestersaldo, 92 = AnstallningBankkontouppgift, 93 = AnstallningKontrolluppgiftsinstallning, 94 = AnstallningPensionOchForsakring, 95 = Uppmarkningskod, 96 = UtbetalningAvLonInstallningLeverantorinformation, 97 = LonBokforingsfilinstallning, 98 = LonSIE4Mall, 99 = LonSIE4Konteringsdimension, 100 = Styrforetag, 101 = ExporteraSaldon, 102 = TripletexIntegration, 103 = EuStatistikLcs, 104 = LonespecifikationerKivra, 105 = LasTurordning, 106 = Semesterberakning, 107 = GranskningAvAnstallningsperiodPaminnelse, 108 = AltinnIntegration, 109 = ExportUrval, 110 = Exportintervall, 111 = ExporturvalHemkontering, 112 = ExporturvalKontering, 113 = ExporturvalUtlaggsurval, 114 = AtkAtfArsskifte, 115 = PowerOfficeGoIntegration, 116 = AtkAtfSkuld, 117 = BkyIntegration, 118 = Ackumulatorskuld, 119 = ScriveSync, 120 = LonekartlaggningCreate, 121 = LonekartlaggningCreateAnstallning, 122 = LonekartlaggningCalculate, 123 = Nyhetsflode, 124 = VerifiedSparaSigneradeDokument, 125 = LonekartlaggningDelete, 126 = VismaNetIntegration, 127 = AutomatiskGranskning, 128 = LonerevisionPaminnelse, 129 = SemesterdagUppdatering, 130 = ScriveSparaSigneradeDokument, 131 = LasTillsvidareCreate, 132 = LasTillsvidareCalculate, 133 = Winningtemp, 134 = RemoveUnmappedKontokort, 135 = LasForetradeCalculate, 140 = PaminnelseNarAllaTidrapporterBlivitGranskade, 141 = EgnaProcesser, 142 = BeraknaBevakningar, 143 = BorttagningAvraknadeReserakningar, 144 = BorttagningAvraknadePeriodavrakningar, 145 = RaderaPersonuppgifter, 146 = EnklaKonverteringar, 147 = VismaNetErp, 148 = VismaConnectRoller, 149 = WebhookSender, 150 = VismaConnectOnboarding, 151 = Bygglosen, 152 = TidBifallAll, 153 = ResBifallAll")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")

class BillingReleaseSelectionAccount(BaseModel):
    code: Optional[str] = Field(None, description="Account code of an account to include in the release")

class BillingReleaseSelectionAccountdistribution(BaseModel):
    accounts: Optional[List[BillingReleaseSelectionAccount]] = Field(None, description="List of specific accounts to include in the release")
    id: Optional[UUID] = Field(None,description="UUID of the account distribution to release")

class BillingReleaseSelectionEmployee(BaseModel):
    employee_number: Optional[str] = Field(None, alias="employeeNumber", description="Employee number to filter the release by.")

class RollbackReleaseModel(BaseModel):
    release_id: Optional[UUID] = Field(None,alias="releaseId",description="UUID of the release")

class BillingReleaseSelectionModel(BaseModel):
    accountdistributions: Optional[List[BillingReleaseSelectionAccountdistribution]] = Field(None, alias="accountdistributions", description="List of account distributions to include in the release.")
    company: UUID = Field(..., description="UUID of the company to release accounts to billing for.")
    employees: Optional[list[BillingReleaseSelectionEmployee]] = Field(None, description="List of employees to filter the release by.")
    invoice_date: Optional[datetime] = Field(None,alias="invoiceDate", description="Date to use as the invoice date for the billing release.")
    release_to_date: Optional[datetime] = Field(None,alias="releaseToDate", description="Release all billable entries up to and including this date.")
    signature: Optional[str] = Field(None, description="Signature or identifier of the user initiating the release.")
    time: Optional[bool] = Field(None,description="Whether to include time entries in the billing release.")
    travel: Optional[bool] = Field(None,description="Whether to include travel entries in the billing release.")

class GetBalances(BaseModel):
    instance: Optional[str] = Field(INSTANCE,description="Domain name")
    company_number: Optional[int] = Field(None,alias="companyNumber",description="Company Number")
    balance_code: Optional[str] = Field(None,alias="balanceCode", description="Balance Code")
    balance_type: Optional[int] = Field(None,alias="balanceType", description="Balance Type:0 = PeriodValue, 1 = OutgoingValue, 2 = IngoingValue")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")

class GetBalancesByCompanyId(BaseModel):
    balance_code: Optional[str] = Field(None,alias="balanceCode", description="Balance Code")
    balance_type: Optional[int] = Field(None,alias="balanceType", description="Balance Type:0 = PeriodValue, 1 = OutgoingValue, 2 = IngoingValue")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")

class BalanceAdjustmentModel(BaseModel):
    adjustment_value: Optional[float] = Field(None, alias="adjustmentValue", description="Adjustment value as a double.")
    balance_adjustment_type: int = Field(..., alias="balanceAdjustmentType", description="Type of balance adjustment. 0 = JusteraUtgaende, 1 = JusteraIngaende, 2 = SattIngaende.")
    balance_code: str = Field(..., alias="balanceCode", min_length=1, description="Balance code.")
    employee_number: str = Field(..., alias="employeeNumber", min_length=1, description="Employee number.")
    entity_description: Optional[str] = Field(None, alias="entityDescription", description="Entity description.")
    flex_sql_sort_order: Optional[int] = Field(None, alias="flexSqlSortOrder", description="FlexSQL sort order: 0 = Ascending, 1 = Descending, -1 = Unspecified ")
    id: Optional[UUID] = Field(None, description="UUID of the balance adjustment.")
    is_generated: bool = Field(..., alias="isGenerated", description="Filter on is generated")
    period_determination_date: datetime = Field(..., alias="periodDeterminationDate", description="Date used to determine the period for this balance adjustment.")

class GetBalanceAdjustmentByEmployeeOrCompany(BaseModel):
    employee_number: Optional[str] = Field(None,alias="employeeNumber",description="Employee number.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")

class GetAbsenceApplicationByParameters(BaseModel):
    employmentnumber: Optional[str] = Field(None,description="Employment number.")
    instance: Optional[str] = Field(None, description="Domain name.")
    companynumber: Optional[int] = Field(None, description="Company number.")
    absence_type_id: Optional[UUID] = Field(None, alias="absenceTypeId", description="UUID of the absence type.")
    absence_type_name: Optional[str] = Field(None, alias="absenceTypeName", description="Name of the absence type.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = ConfigDict(populate_by_name=True)


class GetBalanceAdjustments(BaseModel):
    instance: Optional[str] = Field(None,description="Domain Name")
    companynumber: Optional[int] = Field(None,description="companynumber")
    employee_number: Optional[str] = Field(None,alias="employeeNumber", description="Employee number.")
    balance_code: Optional[str] = Field(None,alias="balanceCode", description="Balance code.")
    adjustment_date: Optional[datetime] = Field(None,alias="adjustmentDate",description="adjustment date")
    adjustment_type: Optional[int] = Field(None,alias="balanceAdjustmentType", description="Type of balance adjustment. 0 = JusteraUtgaende, 1 = JusteraIngaende, 2 = SattIngaende.")
    is_generated: Optional[bool] = Field(None,alias="isGenerated", description="Filter on is generated")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")

class GetBalanceReportByBalanceIdAndEmployeeId(BaseModel):
    employee_id: UUID = Field(None,alias="employeeId",description="UUID of the employee")
    balance_type_value_enum: int = Field(None,alias="balaneTypeValueEnum",description="Type of balance value: 0 = PeriodValue, 1 = OutgoingValue, 2 = IngoingValue")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Get billings from this date")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="Get billings upp to this date.")

class GetBillingReleasesByCompany(BaseModel):
    company: str = Field(...,description="company")
    instance: str = Field(INSTANCE,description="The customer instance (domain)")
    hide_completed_releasees: Optional[bool] = Field(None,description="Hides the billing releases that is fully released")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")

class UserViewModel(BaseModel):
    card_badge_id: Optional[str] = Field(None, alias="cardBadgeId", description="Card bade ID")
    employee_id: Optional[UUID] = Field(None, alias="employeeId", description="UUID of the employee.")
    employee_number: Optional[str] = Field(None, alias="employeeNumber", description="Employee's unique identification number.")
    first_name: Optional[str] = Field(None, alias="firstName", description="Employee's first name.")
    id: Optional[UUID] = Field(None, description="UUID of the user.")
    is_day_reporting_today: Optional[bool] = Field(None, alias="isDayReportingToday", description="Whether the employee is reporting by day today.")
    last_name: Optional[str] = Field(None, alias="lastName", description="Employee's last name.")
    show_week_number: Optional[bool] = Field(None, alias="showWeekNumber", description="Whether to show the week number for this employee.")
    username: Optional[str] = Field(None, alias="username", max_length=100, description="User name")
    username_alias: Optional[str] = Field(None, alias="usernameAlias", description="Alternative username or alias.")

class ChildModel(BaseModel):
    child_country_code: Optional[str] = Field(None,alias="childCountryKod",description="Country code of the child.")
    company_id: UUID = Field(...,alias="companyId",description="UUID of the company")
    employee_id: UUID = Field(...,alias="employeeId",description="UUID of the employee") 
    id: Optional[UUID] = Field(None,description="UUID child")
    identification_string: Optional[str] = Field(None, max_length=100, alias="identificationString", description="Identification string")
    identification_type: Optional[int] = Field(None,alias="identificationType",description="Type of identification: 0 = Birth date, 1 = Social security number, 2 = Optional identification number, 3 = Birth Year")
    instance_id: UUID = Field(..., alias="instanceId",description="Instance Id")
    is_chronically_ill: Optional[bool] = Field(None,alias="isChronicallyIll",description="If the child is chronically ill")
    name: Optional[str] = Field(None, description="Name of the child")
    user: Optional[UserViewModel] = Field(None, )

class GetChildren(BaseModel):
    instance: Optional[str] = Field(None, description="Domain name.")
    company_id: Optional[UUID] = Field(None, alias="companyId", description="Company ID (UUID).")
    company_number: Optional[int] = Field(None, alias="companynumber", description="Company number.")
    employee_id: Optional[UUID] = Field(None, alias="employeeId", description="Employee ID (UUID).")
    employment_number: Optional[str] = Field(None, alias="employmentnumber", description="Employment number.")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")

class CompanyModel(BaseModel):
    company_number: Optional[int] = Field(None, alias="companyNumber", description="Company number.")
    id: Optional[UUID] = Field(None, description="UUID of the company record.")
    is_bky_licensed: Optional[bool] = Field(None, alias="isBkyLicensed", description="Whether the company is licensed for BKY. Nullable.")
    is_coins_licensed: Optional[bool] = Field(None, alias="isCoinsLicensed", description="Whether the company is licensed for Coins. Nullable.")
    is_digital_signering_licensed: Optional[bool] = Field(None, alias="isDigitalSigneringLicensed", description="Whether the company is licensed for Digital Signering (digital signing). Nullable.")
    is_franvarouppfoljning_licensed: Optional[bool] = Field(None, alias="isFranvarouppfoljningLicensed", description="Whether the company is licensed for Franvarouppfoljning (absence tracking). Nullable.")
    is_hr_licensed: Optional[bool] = Field(None, alias="isHrLicensed", description="Whether the company is licensed for HR. Nullable.")
    is_koncern_licensed: Optional[bool] = Field(None, alias="isKoncernLicensed", description="Whether the company is licensed for Koncern (group/corporate). Nullable.")
    is_lonekartlaggning_licensed: Optional[bool] = Field(None, alias="isLonekartlaggningLicensed", description="Whether the company is licensed for Lonekartlaggning (salary mapping). Nullable.")
    is_lonerevision_licensed: Optional[bool] = Field(None, alias="isLonerevisionLicensed", description="Whether the company is licensed for Lonerevision (salary revision). Nullable.")
    is_lonespecifikation_till_kivra_licensed: Optional[bool] = Field(None, alias="isLonespecifikationTillKivraLicensed", description="Whether the company is licensed for sending salary specifications to Kivra. Nullable.")
    is_mobile_licensed: Optional[bool] = Field(None, alias="isMobileLicensed", description="Whether the company is licensed for Mobile. Nullable.")
    is_pay_equity_compass_licensed: Optional[bool] = Field(None, alias="isPayEquityCompassLicensed", description="Whether the company is licensed for Pay Equity Compass. Nullable.")
    is_payroll_licensed: Optional[bool] = Field(None, alias="isPayrollLicensed", description="Whether the company is licensed for Payroll. Nullable.")
    is_plan_licensed: Optional[bool] = Field(None, alias="isPlanLicensed", description="Whether the company is licensed for Plan (scheduling). Nullable.")
    is_qnister_licensed: Optional[bool] = Field(None, alias="isQnisterLicensed", description="Whether the company is licensed for Qnister. Nullable.")
    is_rapportgenerator_licensed: Optional[bool] = Field(None, alias="isRapportgeneratorLicensed", description="Whether the company is licensed for Rapportgenerator (report generator). Nullable.")
    is_statistikcentral_licensed: Optional[bool] = Field(None, alias="isStatistikcentralLicensed", description="Whether the company is licensed for Statistikcentral (statistics center). Nullable.")
    is_time_licensed: Optional[bool] = Field(None, alias="isTimeLicensed", description="Whether the company is licensed for Time. Nullable.")
    is_travel_licensed: Optional[bool] = Field(None, alias="isTravelLicensed", description="Whether the company is licensed for Travel. Nullable.")
    is_winningtemp_licensed: Optional[bool] = Field(None, alias="isWinningtempLicensed", description="Whether the company is licensed for Winningtemp. Nullable.")
    name: Optional[str] = Field(None, description="Company name. Nullable.")
    organization_number: Optional[str] = Field(None, alias="organizationNumber", description="Company organization number. Nullable.")
    start_date: Optional[datetime] = Field(None, alias="startDate", description="Date from which the company is active. Nullable.")

class GetCompanies(BaseModel):
    instance: Optional[str] = Field(INSTANCE,description="Domain Name")
    companynumber: Optional[int] = Field(None,description="companynumber")
    organizationnumber: Optional[int] = Field(None,description="organizationnumber")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")

class CompanyPostRequestModel(BaseModel):
    company_number: int = Field(..., alias="companyNumber", description="Company number.")
    country_code: str = Field(..., alias="countryCode", min_length=1, description="Country code for the company. Minimum length: 1.")
    currency_code: str = Field(..., alias="currencyCode", min_length=1, description="Currency code for the company. Minimum length: 1.")
    is_bky_licensed: Optional[bool] = Field(None, alias="isBkyLicensed", description="Whether the company is licensed for BKY.")
    is_digital_signering_licensed: Optional[bool] = Field(None, alias="isDigitalSigneringLicensed", description="Whether the company is licensed for Digital Signering (digital signing).")
    is_franvarouppfoljning_licensed: Optional[bool] = Field(None, alias="isFranvarouppfoljningLicensed", description="Whether the company is licensed for Franvarouppfoljning (absence tracking).")
    is_hr_licensed: Optional[bool] = Field(None, alias="isHrLicensed", description="Whether the company is licensed for HR.")
    is_koncern_licensed: Optional[bool] = Field(None, alias="isKoncernLicensed", description="Whether the company is licensed for Koncern (group/corporate).")
    is_lonekartlaggning_licensed: Optional[bool] = Field(None, alias="isLonekartlaggningLicensed", description="Whether the company is licensed for Lonekartlaggning (salary mapping).")
    is_lonerevision_licensed: Optional[bool] = Field(None, alias="isLonerevisionLicensed", description="Whether the company is licensed for Lonerevision (salary revision).")
    is_mobile_licensed: Optional[bool] = Field(None, alias="isMobileLicensed", description="Whether the company is licensed for Mobile.")
    is_pay_equity_compass_licensed: Optional[bool] = Field(None, alias="isPayEquityCompassLicensed", description="Whether the company is licensed for Pay Equity Compass.")
    is_payroll_licensed: Optional[bool] = Field(None, alias="isPayrollLicensed", description="Whether the company is licensed for Payroll.")
    is_plan_licensed: Optional[bool] = Field(None, alias="isPlanLicensed", description="Whether the company is licensed for Plan (scheduling).")
    is_qnister_licensed: Optional[bool] = Field(None, alias="isQnisterLicensed", description="Whether the company is licensed for Qnister.")
    is_statistikcentral_licensed: Optional[bool] = Field(None, alias="isStatistikcentralLicensed", description="Whether the company is licensed for Statistikcentral (statistics center).")
    is_time_licensed: Optional[bool] = Field(None, alias="isTimeLicensed", description="Whether the company is licensed for Time.")
    is_travel_licensed: Optional[bool] = Field(None, alias="isTravelLicensed", description="Whether the company is licensed for Travel.")
    is_winningtemp_licensed: Optional[bool] = Field(None, alias="isWinningtempLicensed", description="Whether the company is licensed for Winningtemp.")
    name: str = Field(..., min_length=1, description="Company name. Minimum length: 1.")
    organization_number: Optional[str] = Field(None, alias="organizationNumber", description="Company organization number. Nullable.")

class CustomerModel(BaseModel):
    account_locations: Optional[list[AccountLocationModel]] = Field(None, alias="accountLocations", description="List of geographic locations associated with the customer. Nullable.")
    active_from_date: Optional[datetime] = Field(None, alias="activeFromDate", description="Date from which the customer is active. Nullable.")
    active_tom_date: Optional[datetime] = Field(None, alias="activeTomDate", description="Date until which the customer is active. Nullable.")
    billing: Optional[AccountBillingModel] = Field(None, description="Billing details for the customer.")
    billing_state_enum: Optional[int] = Field(None, alias="billingStateEnum", description="Billing state. 0 = No, 1 = Never, 2 = Yes, 3 = Always.")
    budgeting_time_unit: Optional[int] = Field(None, alias="budgetingTimeUnit", description="Budgeting time unit. 0 = QuarterHour, 1 = HalfHour, 2 = Hour, 3 = Day, 4 = Week, 5 = Month.")
    city: Optional[str] = Field(None, description="City of the customer. Nullable.")
    code: str = Field(..., description="Unique customer code. Minimum length: 1.")
    contact_person: Optional[str] = Field(None, alias="contactperson", description="Contact person at the customer. Nullable.")
    corporate_number: Optional[str] = Field(None, alias="corporatenumber", description="Corporate registration number of the customer. Nullable.")
    country: Optional[str] = Field(None, description="Country of the customer. Nullable.")
    email: Optional[str] = Field(None, description="Email address of the customer. Nullable.")
    external_comment_must_be_stated_about_billable_time: Optional[bool] = Field(None, alias="externalCommentMustBeStatedAboutBillableTime", description="Whether an external comment must be stated about billable time. Nullable.")
    id: Optional[UUID] = Field(None, description="UUID of the customer record.")
    mailing_address: Optional[str] = Field(None, alias="mailingaddress", description="Mailing address of the customer. Nullable.")
    name: str = Field(..., description="Customer name. Minimum length: 1.")
    phone_number: Optional[str] = Field(None, alias="phonenumber", description="Phone number of the customer. Nullable.")
    post_code: Optional[str] = Field(None, alias="postcode", description="Postal code of the customer. Nullable.")
    travel_billing_state_enum: Optional[int] = Field(None, alias="travelBillingStateEnum", description="Travel billing state. 0 = No, 1 = Never, 2 = Yes, 3 = Always.")
    visiting_address: Optional[str] = Field(None, alias="visitingaddress", description="Visiting address of the customer. Nullable.")
    work_place: Optional[WorkplaceModel] = Field(None, alias="workPlace", description="Workplace details associated with the customer.")

class GetCustomersByComopany(BaseModel):
    company: str = Field(..., description="Company number. Required.")
    instance: str = Field(INSTANCE, description="Domain name. Required.")
    code: Optional[str] = Field(None, description="Customer code filter.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    modified_since: Optional[datetime] = Field(None, alias="modifiedSince", description="Filter customers created or modified from this date and time. Format: YYYY-MM-DDTHH:MM:SS.")

class GetCustomersByAccountDistribution (BaseModel):
    code: Optional[str] = Field(None, description="Customer code filter.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    modified_since: Optional[datetime] = Field(None, alias="modifiedSince", description="Filter customers created or modified from this date and time. Format: YYYY-MM-DDTHH:MM:SS.")

class GetTimeScheduleByEmployeeAndDate(BaseModel):
    employee_id: UUID = Field(...,alias="employeeId",description="Employee id as a GUID"),
    date_string: str = Field(...,alias="dateString",description="Date to getdat schedule time from")

class EmploymentModel(BaseModel):
    account_number: Optional[str] = Field(None, alias="accountNumber", description="Bank account number. Nullable.")
    advance_vacation_depreciation_date: Optional[datetime] = Field(None, alias="advanceVacationDepreciationDate", description="Date for advance vacation depreciation. Nullable.")
    advance_vacation_ingoing: Optional[float] = Field(None, alias="advanceVacationIngoing", description="Ingoing advance vacation value. Nullable.")
    auto_calculate_salaries: Optional[bool] = Field(None, alias="autoCalculateSalaries", description="Whether salaries are automatically calculated. Nullable.")
    automatic_calculation_discrete_tax: Optional[bool] = Field(None, alias="automaticCalculationDiscreteTax", description="Whether discrete tax is automatically calculated. Nullable.")
    bic: Optional[str] = Field(None, description="BIC/SWIFT code for international bank transfers. Nullable.")
    clearing_number: Optional[str] = Field(None, alias="clearingNumber", description="Bank clearing number. Nullable.")
    company_number_in_salary_system: Optional[str] = Field(None, alias="companyNumberInSalarySystem", description="Company number as registered in the salary system. Nullable.")
    daily_rest_period_breaking_time: Optional[datetime] = Field(None, alias="dailyRestPeriodBreakingTime", description="Time at which the daily rest period is broken. Nullable.")
    discrete_tax: Optional[float] = Field(None, alias="discreteTax", description="Discrete tax value. Nullable.")
    employment_adjustments_from_date: Optional[datetime] = Field(None, alias="employmentAdjustmentsFromDate", description="Start date for employment salary adjustments. Nullable.")
    employment_adjustments_kronor: Optional[float] = Field(None, alias="employmentAdjustmentsKronor", description="Employment salary adjustment amount in kronor. Nullable.")
    employment_adjustments_percent: Optional[float] = Field(None, alias="employmentAdjustmentsPercent", description="Employment salary adjustment percentage. Nullable.")
    employment_adjustments_to_amount: Optional[float] = Field(None, alias="employmentAdjustmentsToAmount", description="Target amount for employment salary adjustments. Nullable.")
    employment_adjustments_to_date: Optional[datetime] = Field(None, alias="employmentAdjustmentsToDate", description="End date for employment salary adjustments. Nullable.")
    employment_number: Optional[str] = Field(None, alias="employmentNumber", description="Employment number. Nullable.")
    employment_number_in_salary_system: Optional[str] = Field(None, alias="employmentNumberInSalarySystem", description="Employment number as registered in the salary system. Nullable.")
    fixed_balance_adjustment_value: Optional[float] = Field(None, alias="fixedBalanceAdjustmentValue", description="Fixed balance adjustment value. Nullable.")
    has_mobile_license: Optional[bool] = Field(None, alias="hasMobileLicense", description="Whether the employee has a mobile license.")
    has_plan_license: Optional[bool] = Field(None, alias="hasPlanLicense", description="Whether the employee has a plan license.")
    has_time_license: Optional[bool] = Field(None, alias="hasTimeLicense", description="Whether the employee has a time license.")
    has_travel_license: Optional[bool] = Field(None, alias="hasTravelLicense", description="Whether the employee has a travel license.")
    iban: Optional[str] = Field(None, description="IBAN for international bank transfers. Nullable.")
    norwegian_account_number: Optional[str] = Field(None, alias="norwegianAccountNumber", description="Norwegian bank account number. Nullable.")
    regional_aid: Optional[bool] = Field(None, alias="regionalAid", description="Whether the employee is eligible for regional aid. Nullable.")
    research_deduction: Optional[bool] = Field(None, alias="researchDeduction", description="Whether the employee is eligible for research deduction. Nullable.")
    show_in_presence_tableau: Optional[bool] = Field(None, alias="showInPresenceTableau", description="Whether the employee is shown in the presence tableau. Nullable.")
    supplementary_income: Optional[bool] = Field(None, alias="supplementaryIncome", description="Whether the employee has supplementary income. Nullable.")
    tax_column: Optional[int] = Field(None, alias="taxColumn", description="Tax column. 0 = None, 1 = Column1, 2 = Column2, 3 = Column3, 4 = Column4, 5 = Column5, 6 = Column6, 7 = Column7.")
    tax_table: Optional[int] = Field(None, alias="taxTable", description="Tax table. 0 = None, 29 = Table29, 30 = Table30, 31 = Table31, 32 = Table32, 33 = Table33, 34 = Table34, 35 = Table35, 36 = Table36, 37 = Table37, 38 = Table38, 39 = Table39, 40 = Table40, 41 = Table41, 42 = Table42.")
    weekly_rest_breaking_day: Optional[int] = Field(None, alias="weeklyRestBreakingDay", description="Day of the week when weekly rest period is broken. 1 = Monday, 2 = Tuesday, 3 = Wednesday, 4 = Thursday, 5 = Friday, 6 = Saturday, 7 = Sunday.")
    weekly_rest_breaking_time: Optional[datetime] = Field(None, alias="weeklyRestBreakingTime", description="Time at which the weekly rest period is broken. Nullable.")
    work_place_number_scb: Optional[int] = Field(None, alias="workPlaceNumberScb", description="Workplace number as registered with SCB (Statistics Sweden). Nullable.")


class EmployeeModel(BaseModel):
    address_row1: Optional[str] = Field(None, alias="addressRow1", description="First row of the employee's address. Nullable.")
    address_row2: Optional[str] = Field(None, alias="addressRow2", description="Second row of the employee's address. Nullable.")
    city: Optional[str] = Field(None, description="City of the employee's address. Nullable.")
    company_id: Optional[UUID] = Field(None, alias="companyId", description="UUID of the company the employee belongs to.")
    country: Optional[str] = Field(None, description="Country of the employee's address. Nullable.")
    date_of_birth: Optional[datetime] = Field(None, alias="dateOfBirth", description="Employee's date of birth. Nullable.")
    email_private: Optional[str] = Field(None, alias="emailPrivate", description="Employee's private email address. Nullable.")
    email_work: Optional[str] = Field(None, alias="emailWork", description="Employee's work email address. Nullable.")
    employment: Optional[list[EmploymentModel]] = Field(None, description="List of employment records for the employee. Nullable.")
    first_name: Optional[str] = Field(None, alias="firstName", description="Employee's first name. Nullable.")
    gender: Optional[int] = Field(None, description="Employee's gender. 0 = Unknown, 1 = Man, 2 = Woman.")
    id: Optional[UUID] = Field(None, description="UUID of the employee record.")
    immediate_manager_employee_id: Optional[UUID] = Field(None, alias="immediateManagerEmployeeId", description="UUID of the employee's immediate manager. Nullable.")
    instance_id: Optional[UUID] = Field(None, alias="instanceId", description="UUID of the instance this employee belongs to.")
    is_in_audit_process: Optional[bool] = Field(None, alias="isInAuditProcess", description="Whether the employee is currently in an audit process.")
    last_name: Optional[str] = Field(None, alias="lastName", description="Employee's last name. Nullable.")
    mailing_email_private: Optional[bool] = Field(None, alias="mailingEmailPrivate", description="Whether to use private email for mailing. Nullable.")
    mailing_email_work: Optional[bool] = Field(None, alias="mailingEmailWork", description="Whether to use work email for mailing. Nullable.")
    name: Optional[str] = Field(None, description="Employee's full name. Nullable.")
    national_identification_number: Optional[str] = Field(None, alias="nationalIdentificationNumber", description="Employee's national identification number. Nullable.")
    nationality: Optional[str] = Field(None, description="Employee's nationality. Nullable.")
    phone1: Optional[str] = Field(None, description="Employee's primary phone number. Nullable.")
    phone2: Optional[str] = Field(None, description="Employee's secondary phone number. Nullable.")
    phone3: Optional[str] = Field(None, description="Employee's tertiary phone number. Nullable.")
    phone4: Optional[str] = Field(None, description="Employee's quaternary phone number. Nullable.")
    postal_code: Optional[str] = Field(None, alias="postalCode", description="Postal code of the employee's address. Nullable.")
    salary_revision_year: Optional[int] = Field(None, alias="salaryRevisionYear", description="Year of the employee's last salary revision. Nullable.")
    union_id: Optional[UUID] = Field(None, alias="unionId", description="UUID of the union the employee belongs to. Nullable.")

class GetEmployees(BaseModel):
    instance: Optional[str] = Field(INSTANCE, description="Domain name.")
    company_id: Optional[UUID] = Field(None, alias="companyId", description="Company ID (UUID).")
    company_number: Optional[int] = Field(None, alias="companynumber", description="Company number.")
    employment_number: Optional[str] = Field(None, alias="employmentnumber", description="Employment number.")
    email: Optional[str] = Field(None, description="Email address of the employee.")
    modified_since: Optional[datetime] = Field(None, alias="modifiedSince", description="Filter employees created or modified from this date and time. Format: YYYY-MM-DDTHH:MM:SS.")
    national_identification_number: Optional[str] = Field(None, alias="nationalIdentificationNumber", description="Filter employees by national identification number.")
    is_in_audit_process: Optional[bool] = Field(None, alias="isInAuditProcess", description="Filter employees by whether they are currently in an audit process.")
    employment_type: Optional[int] = Field(None, alias="employmentType", description="Filter employees by employment type of their current employment period.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")

class EmployeeCreateParams(BaseModel):
    employementtemplate_id: UUID = Field(None,alias="employementtemplateId",description="Create employee with use of selected employment template. If left empty then company default template will be used.")
    employment_period_start: datetime = Field(None,alias="employmentPeriodStart",description="Set start date of the default employmentPeriod created. Must be specified for the employment templates assignment template to be applied.")
    employement_period_end: datetime = Field(None,alias="employmentPeriodEnd",description="Set end date of the default employmentPeriod created.")

class EmployeeCreateModel(EmployeeModel):
    email_visma_connect: Optional[str] = Field(None, alias="emailVismaConnect", description="Employee's Visma Connect email address used for system authentication. Nullable.")

class EmployeeImageModel(BaseModel):
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company the employee belongs to.")
    compressed_image: Optional[str] = Field(None, alias="compressedImage", description="Compressed version of the employee image as a base64 encoded string. Nullable.")
    employee_id: UUID = Field(..., alias="employeeId", description="UUID of the employee.")
    id: Optional[UUID] = Field(None, description="UUID of the employee image record.")
    image: str = Field(..., min_length=1, description="Employee image as a base64 encoded string. Minimum length: 1.")

class GetEmployeeImgaes(BaseModel):
    employee_id: Optional[UUID] = Field(None, alias="employeeId", description="UUID of the employee")
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")



class TimeCode(BaseModel):
    code:str

class TimeRow(BaseModel):
    start: Optional[datetime] = Field(
        None,
        alias="fromTimeDateTime",
        description=(
            "Start time of the work period (ISO 8601 datetime)."
        )
    )
    end: Optional[datetime] = Field(
        None,
        alias="toTimeDateTime",
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
    time_code: Optional[TimeCode] = Field(
        None,
        alias="timeCode",
        description="Optional time code (e.g. 'WORK', 'OVERTIME')."
    )
    comment: Optional[str] = Field(
        None,
        description="Optional comment for the time entry."
    )
 
    model_config = {"populate_by_name": True}

    @field_serializer("start", "end")
    def serialize_datetime(self, value: datetime):
        return value.replace(tzinfo=None).isoformat(timespec="milliseconds") + "Z"
    
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
    account_id: UUID = Field(None,alias="accountId", description="UUID of the account.")
    account_distribution_id: UUID = Field(None,alias="accountDistributionId", description="UUID of the account distribution.")
    account_code: Optional[str] = Field(None, alias="accountCode", description="Account code string.")
    put_blank: Optional[bool] = Field(None, alias="putBlank", description="Whether to put a blank value for this account.")
    rule_enum: Optional[int] = Field(
        None,
        alias="ruleEnum",
        description="Distribution rule. 0 = CanBeSpecified, 1 = MustBeSpecified, 2 = Locked, -1 = Inheritance."
    )
 
    model_config = {"populate_by_name": True}
 
class BillingPriceRowAccount(BaseModel):
    account_id: UUID = Field(None,alias="accountId", description="UUID of the account.")
    id: UUID = Field(None,description="UUID of the price row account entry.")
 
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
    limit: float = Field(None,description="The threshold value for the control.")
    summary: int = Field(None,description="Control summary scope. 0 = Hierarchic, 1 = Individual.")
    type: int = Field(None,description="Control type. 0 = Warning, 1 = Error.")
 
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
    code: str = Field(None,min_length=1, description="Project code. Required.")
    name: str = Field(None,min_length=1, description="Project name. Required.")
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
    account_locations: Optional[list[AccountLocationModel]] = Field(
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
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")

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
    instance: Optional[str] = Field(None,description="Domain name.")
    company_id: Optional[UUID] = Field(None,description="Company id.")
    company_number: Optional[int] = Field(None,description="Company number.")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")
    model_config = ConfigDict(populate_by_name=True)

class ListCompaniesInput(BaseModel):
    instance: Optional[str] = Field(
        default=DOMAIN,
        description="Domain name. If not provided, defaults to the default-domain instance."
    )
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = ConfigDict(populate_by_name=True)

class GetUsers(BaseModel):
    instance: Optional[str] = Field(INSTANCE, description="Domain name.")
    username: Optional[str] = Field(None, description="User name.")
    extern_ref: Optional[str] = Field(None, description="External reference.")
    user_type: Optional[int] = Field(None, description="User type: 1 = System, 2 = Instance") 
    active: Optional[bool] = Field(None, description="Are the useres active.")
    logon_since: Optional[datetime] = Field(None, description="Did the user log in since.")
    no_logon_since: Optional[datetime] = Field(None, description="Did the user not log in since.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = ConfigDict(populate_by_name=True)

class GetUsersByInstance(GetUsers):
    instance: str = Field(INSTANCE, description="Domain name.")

class GetVehicleTypes(BaseModel):
    company_id: Optional[UUID] = Field(None, alias="companyId", description="Company ID (UUID).")
    vechile_type: Optional[int] = Field(None, alias="vehicleType", description="Vehicle type string to search for: 0 = Private, 1 = Business")
    comsumption_unit: Optional[int] = Field(None, alias="consumptionUnit", description="Consumption unit: 0 = LPer100Km, 1 = KWhPer100Km")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = ConfigDict(populate_by_name=True)

class GetAllQualifications(BaseModel):
    instance: Optional[str] = Field(None, description="Domain name.")
    company_id: Optional[UUID] = Field(None, alias="companyId", description="Company ID (UUID).")
    company_number: Optional[int] = Field(None, alias="companyNumber", description="Company number.")
    employee_id: Optional[UUID] = Field(None, alias="employeeId", description="UUID of employees with this qualification. Nullable.")
    employment_number: Optional[str] = Field(None, alias="employmentNumber", description="Employment number.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")

class GetVehicleTypeByCompanyId(GetVehicleTypes):
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
    instance: Optional[str] = Field(description="Domain name.")
    company_number: Optional[int] = Field(None, alias="companyNumber", description="Company number.")
    employment_number: Optional[str] = Field(None, alias="employmentNumber", description="Employment number.")
    payment_from_date: Optional[datetime] = Field(None, alias="paymentFromDate", description="Payment from date.")
    payment_to_date: Optional[datetime] = Field(None, alias="paymentToDate", description="Payment to date.")
    audit_from_date: Optional[datetime] = Field(None, alias="auditFromDate", description="Audit from date. Will check all audit levels if publicTravelClaimAuditLevelId is not specified.")
    audit_to_date: Optional[datetime] = Field(None, alias="auditToDate", description="Audit to date. Will check all audit levels if publicTravelClaimAuditLevelId is not specified.")
    public_travel_claim_audit_level_id: Optional[UUID] = Field(None, alias="publicTravelClaimAuditLevelId", description="UUID of the public travel claim audit level.  Must be used in combination with atleast one of auditFromDate/auditToDate. If not specified, will check all audit levels.")
    billing_release_from_date: Optional[datetime] = Field(None, alias="billingReleaseFromDate", description="Get travel claims by billing release from date-time.")
    billing_release_to_date: Optional[datetime] = Field(None, alias="billingReleaseToDate", description="Get travel claims by billing release to date-time.")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")
    model_config = ConfigDict(populate_by_name=True)



