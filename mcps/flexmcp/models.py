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
    page_index: Optional[int] = Field(0, alias="pageIndex", description="Page index dafault value 0.")
    page_size: Optional[int] = Field(20, alias="pageSize", description="Page size dafault value 20.")
    model_config = {"populate_by_name": True}

class AbsenceStatusModel(BaseModel):
    absence_application_id: UUID = Field(..., alias="absenceApplicationId", description="UUID of the absence application.")
    id: UUID = Field(..., description="UUID of this status record.")
    message: Optional[str] = Field(None, description="Message from the approver regarding the absence application.")
    status: int = Field(..., description="Status of the absence application.") #Hittar inte vilka int som motsvarar vad
    time_stamp: datetime = Field(..., alias="timeStamp", description="Timestamp of the absence status.")
    user_id: UUID = Field(..., alias="userId", description="UUID of the user who made the status update.")
    user_signature: Optional[str] = Field(None, alias="userSignature", description="Signature of the user who made the status update.")
    model_config = {"populate_by_name": True}

class WorkplaceModel(BaseModel):
    adress: Optional[str] = Field(None, description="Adress of the workplace")
    city: Optional[str] = Field(None,description="City of the workspace")
    country: Optional[str] = Field(None,description="Country of the workspace")
    postal_code: Optional[str] = Field(None,alias="postalCode",description="Postal code of the workplace")
    type: Optional[int] = Field(None, description="Type of workspace: 0 = Physical, 1 = Remote, 2 = NotFixed")
    model_config = {"populate_by_name": True}

class CreateAbsenceApplicationQuery(BaseModel):
    apply_approval: Optional[bool] = Field(False, alias="applyApproval", description="Decides whether the absence application has automatic approval to the highest level. Default value false.")
    is_part_time_absence: Optional[bool] = Field(False, alias="isPartTimeAbsence", description="Decides whether the absence application is part time absence. Default false.")
    model_config = {"populate_by_name": True}

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
    model_config = {"populate_by_name": True}

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
    model_config = {"populate_by_name": True}

class AccountBillingModel(BaseModel):
    price_rows: Optional[list[AccountBillingPriceRowModel]] = Field([], alias="priceRows", description="List of standard billing price rows. Nullable.")
    price_rows_travel: Optional[list[AccountBillingPriceRowModel]] = Field([], alias="priceRowsTravel", description="List of travel billing price rows. Nullable.")
    model_config = {"populate_by_name": True}

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
    model_config = {"populate_by_name": True}

class GetAccountBudgetByAccountId(BaseModel):
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="From date. Get account budget from date.")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="From date. Get account budget from date.")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")
    model_config = {"populate_by_name": True}

class AccountBudgetModel(BaseModel):
    actual_sales: float = Field(...,alias="actualSales",description="The observed sales")
    budgeted_cost: float = Field(...,alias="budgetedCost",description="The budgeted costs")
    budgeted_hours: float = Field(...,alias="budgetedHours",description="The budgeted hours")
    budgeted_sales: float = Field(...,alias="budgetedSales",description="The budgeted sales")
    date_time: str = Field(...,min_length=1,alias="dateTime",description="Budget period identifier as a string.")
    id: UUID = Field(None, description="UUID of the Account budget")
    model_config = {"populate_by_name": True}

class AccountModel(BaseModel):
    account_locations: Optional[List[AccountLocationModel]] = Field([], alias="accountLocations", description="A list of account locations")
    active_from_date: Optional[datetime] = Field(None,alias="activeFromDate",description="Account active from date")
    active_to_date: Optional[datetime] = Field(None,alias="activeTomDate",description="Account active to date")
    billing: Optional[AccountBillingModel] = Field(AccountBillingModel(), description="billing")
    billing_state_enum: Optional[int] = Field(None,alias="billingStateEnum",description="Billing state: 0 = No, 1 = Never, 2 = Yes, 3 = Always")
    budgeting_time_unit: Optional[int] = Field(None,alias="budgetingTimeUnit", description="Budgeting time unit. 0 = QuarterHour, 1 = HalfHour, 2 = Hour, 3 = Day, 4 = Week, 5 = Month.")
    code: str = Field(None, min_length=1, description="Unique account code")
    external_comment_must_be_stated_about_billable_time: Optional[bool] = Field(None, alias="externalCommentMustBeStatedAboutBillableTime", description="Whether an external comment must be stated about billable time.")
    id: Optional[UUID] = Field(None, description="UUID of the account.")
    name: str = Field(..., description="Account name. Minimum length: 1.")
    travel_billing_state_enum: Optional[int] = Field(None, alias="travelBillingStateEnum", description="Travel billing state. 0 = No, 1 = Never, 2 = Yes, 3 = Always.")
    work_place: Optional[WorkplaceModel] = Field(None, alias="workPlace", description="Workplace details associated with the account.")
    model_config = {"populate_by_name": True}

class GetAbsenceTypes(BaseModel):
    page_params: PageModel = PageModel()
    absence_type_name: Optional[str] = Field(None, alias="absenceTypeName", description="Name of the absence type.")
    model_config = {"populate_by_name": True}

class UpdateAbsenceApplicationQuery(BaseModel):
    apply_approval: Optional[bool] = Field(False, alias="applyApproval", description="Decides whether the absence application has automatic approval to the highest level. Default value false.")
    is_part_time_absence: Optional[bool] = Field(False, alias="isPartTimeAbsence", description="Decides whether the absence application is part time absence. Default false.")
    model_config = ConfigDict(populate_by_name=True)
    model_config = {"populate_by_name": True}

class AccountCombinationAccountModel(BaseModel):
    account_distribution: UUID = Field(...,alias="accountDistribution",description="UUID of the account distribution")
    account_selection: str = Field(...,min_length=1,alias="accountSelection",description="Code identifying the selected account within the distribution.")
    model_config = {"populate_by_name": True}

class AccountCombinationModel(BaseModel):
    account_combination_accounts: Optional[List[AccountCombinationAccountModel]] = Field(None,alias="accountCombinationAccounts",description="List of combination accounts")
    combination_rule: int = Field(...,alias="combinationRule",description="Whether or not to allow posting combination: 1 = Allow, -1 = Do not Allow")
    company_id: UUID = Field(...,alias="companyId",description="UUID of the company")
    model_config = {"populate_by_name": True}

class GetAccountDistribution(BaseModel):
    company: str = Field(...,description="Company number")
    instance: str = Field(INSTANCE,description="Domain name")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")
    model_config = {"populate_by_name": True}

class AccountDistributionPartApprovalPermissionModel(BaseModel):
    account_distribution_id: UUID = Field(...,alias="accountDistributionId",description="UUID of the account distribution")
    id: UUID = Field(...,description="Part approval Permisson id")
    premission_to_account_without_row_or_account: bool = Field(...,alias="premissionToAccountWithoutRowOrAccount",description="Whether the user has permission to approve account distributions without a specified row or account.")
    premission_to_all_accounts: bool = Field(..., alias="premissionToAllAccounts", description="Whether the user has permission to approve all accounts.")
    user_id: UUID = Field(..., alias="userId", description="UUID of the user this permission applies to.")
    model_config = {"populate_by_name": True}

class GetCompanyAccountApprovalPermississons(BaseModel):
    instance: Optional[str] = Field(None,description="instance")
    companynumber: Optional[int] = Field(None,description="companynumber")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")
    user_id: Optional[UUID] = Field(None,alias="userId",description="UUID of the user")
    model_config = {"populate_by_name": True}

class GetAccumulators(BaseModel):
    company_id: Optional[UUID] = Field(None,alias="companyId",description="UUID of the company")
    accumulator_type: Optional[int] = Field(None,alias="accumulatorType",description="Type of the accumulator:0 = None, 1 = Gross, 2 = Benefit, 3 = Tax, 4 = Allowance, 5 = Deduction, 6 = DebtGross, 7 = DebtNet")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")
    model_config = {"populate_by_name": True}

class GetAllowanceRuleSet(BaseModel):
    company_id: Optional[UUID] = Field(None,alias="companyId",description="UUID of the company")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")
    model_config = {"populate_by_name": True}

class GetAuditedTimeReportsByCompany(BaseModel):
    salary_transfer_id: Optional[UUID] = Field(None,alias="salartTransferId",description="Get time reports that have been sent to salary using the salary tranfer id")
    from_date: Optional[datetime] = Field(None,alias="fromDate",description="Time reports reported after this date")
    to_date: Optional[datetime] = Field(None,alias="fromDate", description="Time reports reported before this date")
    approved_from_date: Optional[datetime] = Field(None,alias="approvedFromDate",description="Get time reports that have been audited after this date")
    approved_to_date: Optional[datetime]  = Field(None,alias="approvedToDate",description="Get time reports that have been audited before this date")
    audit_level_id: Optional[str] = Field(None,alias="auditLevelId",description="Get time reports that have been audited with this audit level id. If empty all audit levels will be selected")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")
    model_config = {"populate_by_name": True}

class GetTimeReportByEmployee(BaseModel):
    employee_id: UUID = Field(..., alias="employeeId", description="employee id")
    date: Optional[datetime] = Field(None, description="Time reports reported after this date")
    generated: Optional[bool] = Field(True, description="Include generated time rows")
    model_config = ConfigDict(populate_by_name=True)
    model_config = {"populate_by_name": True}

class GetBackGroundTasks(BaseModel):
    worker_state: Optional[int] = Field(None,alias="workerState", description="Worker state of the background task: 0 = Enqueued, 1 = Scheduled, 2 = Processing, 3 = Succeeded, 4 = Failed, 5 = Deleted, 6 = Awaiting")
    worker_function: Optional[int] = Field(None,alias="workerFunction", description="Function of the worker: 0 = None, 1 = Exempelfunktion, 2 = Dygnsrutin, 3 = Mailer, 4 = ValutakursImport, 5 = PaminnelseTidrapport, 6 = Paminnelse, 7 = RensaReserakningar, 8 = RensaTidrapporter, 9 = UtrikesTraktamenteImport, 10 = CreateForetag, 11 = ResaLoneoverforing, 12 = TidLoneoverforing, 13 = CreateForetagsinstallningarFil, 14 = Importmallsimport, 15 = DeleteForetag, 16 = DeleteKundinstans, 17 = DeleteForetagsinstallningarFil, 18 = OverwriteForetag, 19 = Lonekorning, 20 = FrislappTillFakturering, 21 = JeevesQueueSender, 22 = RollbackFrislappTillFakturering, 23 = FirstCardFileRetreivalAndKontokortImport, 24 = EurocardKontokortImport, 25 = Meddelanden, 26 = SkattetabellImport, 27 = Export, 28 = SchemalagdKorning, 29 = UppdateraAckumulator, 30 = ExportAnstalld, 31 = RefreshTidrapporter, 32 = Lonerevision, 33 = CalculateLonekorningAnstallning, 34 = UpdateDatabase, 35 = FortnoxKonteringsimport, 36 = DanskeBankKontokortImport, 37 = FortnoxBokforingsoverforing, 38 = TidDelbifall, 39 = RecalculateReserakningar, 40 = KopieraSchema, 41 = FlexOnlineSystemInformationSender, 42 = AutoBemanning, 43 = Felmeddelandeutskick, 44 = LonBokforingsunderlag, 45 = Kontrolluppgifter, 46 = UpdateNarvarotablaData, 47 = InitiatePayroll, 48 = Semesterarsskifte, 49 = SenAnkomstPaminnelse, 50 = UtbetalningAvLon, 51 = AnonymiseringPersonuppgifter, 52 = Semesterskuld, 53 = PassforfraganAnswer, 54 = Formel, 55 = TidregistreringAvvikelseinstallning, 56 = Tidregistreringsinstallning, 57 = TidregistreringStamplinginstallning, 58 = TidrapporteringColumnLayoutinstallning, 59 = TidregistreringAvvikelsetyperInstallning, 60 = Agi, 61 = Kontokortsfil, 62 = KvittoScanning, 63 = SprakFilerFromFlexOnline, 64 = StandardvardenForDynamiskOversattningFromFlexOnline, 65 = StandardvardenForDynamiskOversattningTillFlexOnline, 66 = FlexKontokort, 67 = PensionOchForsakring, 68 = LonerevisionClearInactiveRowLocks, 69 = LicensFromFlexOnline, 70 = XledgerIntegration, 71 = Onboarding, 72 = UteblivenStamplingPaminnelse, 73 = UteblivenStamplingPaminnelseScheduler, 74 = Arbetsgivarintyg, 75 = FragaOmSkatteavdrag, 76 = KonjunkturstatistikKLP, 77 = KopieraForetag, 79 = OfflineStamplingar, 80 = KonjunkturstatistikKSju, 81 = KonjunkturstatistikKSP, 82 = LonestrukturstatistikSLP, 83 = CalculateTidrapportdagDataWorkerService, 84 = ResetTidrapportdagDataWorkerService, 85 = Retrolon, 86 = KomprimeraBilagor, 87 = VerifiedSync, 88 = AnstallningSemesterinstallning, 89 = AnstallningSemesterarIngaendeVarde, 90 = AnstallningSemesterarSemestersaldo, 91 = LonekorningAnstallningSemesterarSemestersaldo, 92 = AnstallningBankkontouppgift, 93 = AnstallningKontrolluppgiftsinstallning, 94 = AnstallningPensionOchForsakring, 95 = Uppmarkningskod, 96 = UtbetalningAvLonInstallningLeverantorinformation, 97 = LonBokforingsfilinstallning, 98 = LonSIE4Mall, 99 = LonSIE4Konteringsdimension, 100 = Styrforetag, 101 = ExporteraSaldon, 102 = TripletexIntegration, 103 = EuStatistikLcs, 104 = LonespecifikationerKivra, 105 = LasTurordning, 106 = Semesterberakning, 107 = GranskningAvAnstallningsperiodPaminnelse, 108 = AltinnIntegration, 109 = ExportUrval, 110 = Exportintervall, 111 = ExporturvalHemkontering, 112 = ExporturvalKontering, 113 = ExporturvalUtlaggsurval, 114 = AtkAtfArsskifte, 115 = PowerOfficeGoIntegration, 116 = AtkAtfSkuld, 117 = BkyIntegration, 118 = Ackumulatorskuld, 119 = ScriveSync, 120 = LonekartlaggningCreate, 121 = LonekartlaggningCreateAnstallning, 122 = LonekartlaggningCalculate, 123 = Nyhetsflode, 124 = VerifiedSparaSigneradeDokument, 125 = LonekartlaggningDelete, 126 = VismaNetIntegration, 127 = AutomatiskGranskning, 128 = LonerevisionPaminnelse, 129 = SemesterdagUppdatering, 130 = ScriveSparaSigneradeDokument, 131 = LasTillsvidareCreate, 132 = LasTillsvidareCalculate, 133 = Winningtemp, 134 = RemoveUnmappedKontokort, 135 = LasForetradeCalculate, 140 = PaminnelseNarAllaTidrapporterBlivitGranskade, 141 = EgnaProcesser, 142 = BeraknaBevakningar, 143 = BorttagningAvraknadeReserakningar, 144 = BorttagningAvraknadePeriodavrakningar, 145 = RaderaPersonuppgifter, 146 = EnklaKonverteringar, 147 = VismaNetErp, 148 = VismaConnectRoller, 149 = WebhookSender, 150 = VismaConnectOnboarding, 151 = Bygglosen, 152 = TidBifallAll, 153 = ResBifallAll")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")
    model_config = {"populate_by_name": True}

class BillingReleaseSelectionAccount(BaseModel):
    code: Optional[str] = Field(None, description="Account code of an account to include in the release")
    model_config = {"populate_by_name": True}

class BillingReleaseSelectionAccountdistribution(BaseModel):
    accounts: Optional[List[BillingReleaseSelectionAccount]] = Field(None, description="List of specific accounts to include in the release")
    id: Optional[UUID] = Field(None,description="UUID of the account distribution to release")
    model_config = {"populate_by_name": True}

class BillingReleaseSelectionEmployee(BaseModel):
    employee_number: Optional[str] = Field(None, alias="employeeNumber", description="Employee number to filter the release by.")
    model_config = {"populate_by_name": True}

class RollbackReleaseModel(BaseModel):
    release_id: Optional[UUID] = Field(None,alias="releaseId",description="UUID of the release")
    model_config = {"populate_by_name": True}

class BillingReleaseSelectionModel(BaseModel):
    accountdistributions: Optional[List[BillingReleaseSelectionAccountdistribution]] = Field(None, alias="accountdistributions", description="List of account distributions to include in the release.")
    company: UUID = Field(..., description="UUID of the company to release accounts to billing for.")
    employees: Optional[list[BillingReleaseSelectionEmployee]] = Field(None, description="List of employees to filter the release by.")
    invoice_date: Optional[datetime] = Field(None,alias="invoiceDate", description="Date to use as the invoice date for the billing release.")
    release_to_date: Optional[datetime] = Field(None,alias="releaseToDate", description="Release all billable entries up to and including this date.")
    signature: Optional[str] = Field(None, description="Signature or identifier of the user initiating the release.")
    time: Optional[bool] = Field(None,description="Whether to include time entries in the billing release.")
    travel: Optional[bool] = Field(None,description="Whether to include travel entries in the billing release.")
    model_config = {"populate_by_name": True}

class GetBalances(BaseModel):
    instance: Optional[str] = Field(INSTANCE,description="Domain name")
    company_number: Optional[int] = Field(None,alias="companyNumber",description="Company Number")
    balance_code: Optional[str] = Field(None,alias="balanceCode", description="Balance Code")
    balance_type: Optional[int] = Field(None,alias="balanceType", description="Balance Type:0 = PeriodValue, 1 = OutgoingValue, 2 = IngoingValue")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")
    model_config = {"populate_by_name": True}

class GetBalancesByCompanyId(BaseModel):
    balance_code: Optional[str] = Field(None,alias="balanceCode", description="Balance Code")
    balance_type: Optional[int] = Field(None,alias="balanceType", description="Balance Type:0 = PeriodValue, 1 = OutgoingValue, 2 = IngoingValue")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")
    model_config = {"populate_by_name": True}

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
    model_config = {"populate_by_name": True}

class GetBalanceAdjustmentByEmployeeOrCompany(BaseModel):
    employee_number: Optional[str] = Field(None,alias="employeeNumber",description="Employee number.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = {"populate_by_name": True}

class GetAbsenceApplicationByParameters(BaseModel):
    employmentnumber: Optional[str] = Field(None,description="Employment number.")
    instance: Optional[str] = Field(None, description="Domain name.")
    companynumber: Optional[int] = Field(None, description="Company number.")
    absence_type_id: Optional[UUID] = Field(None, alias="absenceTypeId", description="UUID of the absence type.")
    absence_type_name: Optional[str] = Field(None, alias="absenceTypeName", description="Name of the absence type.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = ConfigDict(populate_by_name=True)
    model_config = {"populate_by_name": True}


class GetBalanceAdjustments(BaseModel):
    instance: Optional[str] = Field(None,description="Domain Name")
    companynumber: Optional[int] = Field(None,description="companynumber")
    employee_number: Optional[str] = Field(None,alias="employeeNumber", description="Employee number.")
    balance_code: Optional[str] = Field(None,alias="balanceCode", description="Balance code.")
    adjustment_date: Optional[datetime] = Field(None,alias="adjustmentDate",description="adjustment date")
    adjustment_type: Optional[int] = Field(None,alias="balanceAdjustmentType", description="Type of balance adjustment. 0 = JusteraUtgaende, 1 = JusteraIngaende, 2 = SattIngaende.")
    is_generated: Optional[bool] = Field(None,alias="isGenerated", description="Filter on is generated")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")
    model_config = {"populate_by_name": True}

class GetBalanceReportByBalanceIdAndEmployeeId(BaseModel):
    employee_id: UUID = Field(None,alias="employeeId",description="UUID of the employee")
    balance_type_value_enum: int = Field(None,alias="balaneTypeValueEnum",description="Type of balance value: 0 = PeriodValue, 1 = OutgoingValue, 2 = IngoingValue")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Get billings from this date")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="Get billings upp to this date.")
    model_config = {"populate_by_name": True}

class GetBillingReleasesByCompany(BaseModel):
    company: str = Field(...,description="company")
    instance: str = Field(INSTANCE,description="The customer instance (domain)")
    hide_completed_releasees: Optional[bool] = Field(None,description="Hides the billing releases that is fully released")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")
    model_config = {"populate_by_name": True}

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
    model_config = {"populate_by_name": True}

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
    model_config = {"populate_by_name": True}

class GenericGetModel(BaseModel):
    instance: Optional[str] = Field(None, description="Domain name.")
    company_id: Optional[UUID] = Field(None, alias="companyId", description="Company ID (UUID).")
    company_number: Optional[int] = Field(None, alias="companynumber", description="Company number.")
    employee_id: Optional[UUID] = Field(None, alias="employeeId", description="Employee ID (UUID).")
    employment_number: Optional[str] = Field(None, alias="employmentnumber", description="Employment number.")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")
    model_config = {"populate_by_name": True}

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
    model_config = {"populate_by_name": True}

class GetCompanies(BaseModel):
    instance: Optional[str] = Field(None, description="Domain Name")
    companynumber: Optional[int] = Field(None, description="companynumber")
    organizationnumber: Optional[int] = Field(None,description="organizationnumber")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")
    model_config = ConfigDict(populate_by_name=True)
    model_config = {"populate_by_name": True}

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
    model_config = {"populate_by_name": True}

class CustomerModel(BaseModel):
    account_locations: Optional[list[AccountLocationModel]] = Field(None, alias="accountLocations", description="List of geographic locations associated with the customer. Nullable.")
    active_from_date: Optional[datetime] = Field(None, alias="activeFromDate", description="Date from which the customer is active. Nullable.")
    active_to_date: Optional[datetime] = Field(None, alias="activeTomDate", description="Date until which the customer is active. Nullable.")
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
    model_config = {"populate_by_name": True}

class GetCustomersByComopany(BaseModel):
    company: str = Field(..., description="Company number. Required.")
    instance: str = Field(INSTANCE, description="Domain name. Required.")
    code: Optional[str] = Field(None, description="Customer code filter.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    modified_since: Optional[datetime] = Field(None, alias="modifiedSince", description="Filter customers created or modified from this date and time. Format: YYYY-MM-DDTHH:MM:SS.")
    model_config = {"populate_by_name": True}

class GetCustomersByAccountDistribution (BaseModel):
    code: Optional[str] = Field(None, description="Customer code filter.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    modified_since: Optional[datetime] = Field(None, alias="modifiedSince", description="Filter customers created or modified from this date and time. Format: YYYY-MM-DDTHH:MM:SS.")
    model_config = {"populate_by_name": True}

class GetTimeScheduleByEmployeeAndDate(BaseModel):
    employee_id: UUID = Field(...,alias="employeeId",description="Employee id as a GUID")
    date_string: str = Field(...,alias="dateString",description="Date to getdat schedule time from")
    model_config = {"populate_by_name": True}

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
    model_config = {"populate_by_name": True}

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
    model_config = {"populate_by_name": True}

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
    model_config = {"populate_by_name": True}

class EmployeeCreateParams(BaseModel):
    employementtemplate_id: UUID = Field(None,alias="employementtemplateId",description="Create employee with use of selected employment template. If left empty then company default template will be used.")
    employment_period_start: datetime = Field(None,alias="employmentPeriodStart",description="Set start date of the default employmentPeriod created. Must be specified for the employment templates assignment template to be applied.")
    employement_period_end: datetime = Field(None,alias="employmentPeriodEnd",description="Set end date of the default employmentPeriod created.")
    model_config = {"populate_by_name": True}

class EmployeeCreateModel(EmployeeModel):
    email_visma_connect: Optional[str] = Field(None, alias="emailVismaConnect", description="Employee's Visma Connect email address used for system authentication. Nullable.")
    model_config = {"populate_by_name": True}

class EmployeeImageModel(BaseModel):
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company the employee belongs to.")
    compressed_image: Optional[str] = Field(None, alias="compressedImage", description="Compressed version of the employee image as a base64 encoded string. Nullable.")
    employee_id: UUID = Field(..., alias="employeeId", description="UUID of the employee.")
    id: Optional[UUID] = Field(None, description="UUID of the employee image record.")
    image: str = Field(..., min_length=1, description="Employee image as a base64 encoded string. Minimum length: 1.")
    model_config = {"populate_by_name": True}

class GetEmployeeImgaes(BaseModel):
    employee_id: Optional[UUID] = Field(None, alias="employeeId", description="UUID of the employee")
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = {"populate_by_name": True}

class EmployeeQualificationModel(BaseModel):
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    employee_id: UUID = Field(..., alias="employeeId", description="UUID of the employee.")
    id: Optional[UUID] = Field(None, description="UUID of the employee qualification record.")
    instance_id: UUID = Field(..., alias="instanceId", description="UUID of the instance.")
    qualification_id: UUID = Field(..., alias="qualificationId", description="UUID of the qualification.")
    qualification_level: float = Field(..., alias="qualificationLevel", description="Level of the employee's qualification.")
    model_config = {"populate_by_name": True}

class EmploymentDefaultAccountModel(BaseModel):
    account_code: Optional[str] = Field(None, alias="accountCode", description="Account code. Nullable.")
    account_distribution_id: Optional[UUID] = Field(None, alias="accountDistributionId", description="UUID of the account distribution.")
    account_id: Optional[UUID] = Field(None, alias="accountId", description="UUID of the account. Nullable.")
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    employee_id: UUID = Field(..., alias="employeeId", description="UUID of the employee.")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Start date of the default account validity period. Nullable.")
    id: Optional[UUID] = Field(None, description="UUID of the employment default account record.")
    instance_id: UUID = Field(..., alias="instanceId", description="UUID of the instance.")
    to_date: Optional[datetime] = Field(None, alias="tomDate", description="End date of the default account validity period. Nullable.")
    model_config = {"populate_by_name": True}

class EmploymentDefaultAccountModelBase(BaseModel):
    account_code: Optional[str] = Field(None, alias="accountCode", description="Account code. Nullable.")
    account_distribution_id: Optional[UUID] = Field(None, alias="accountDistributionId", description="UUID of the account distribution.")
    account_id: Optional[UUID] = Field(None, alias="accountId", description="UUID of the account. Nullable.")
    id: Optional[UUID] = Field(None, description="UUID of the employment default account record.")
    model_config = {"populate_by_name": True}

class EmploymentDefaultAccountIntervalModel(BaseModel):
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    employee_id: UUID = Field(..., alias="employeeId", description="UUID of the employee.")
    employee_number: Optional[str] = Field(None, alias="employeeNumber", description="Employee number. Nullable.")
    employment_default_account: Optional[list[EmploymentDefaultAccountModelBase]] = Field(None, alias="employmentDefaultAccount", description="List of default accounts for this employment interval. Nullable.")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Start date of the employment default account interval. Nullable.")
    id: Optional[UUID] = Field(None, description="UUID of the employment default account interval record.")
    instance_id: UUID = Field(..., alias="instanceId", description="UUID of the instance.")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="End date of the employment default account interval. Nullable.")
    model_config = {"populate_by_name": True}

class GetEmploymentDocumentCollection(BaseModel):
    company_id: UUID = Field(...,alias="companyId",description="UUID of the company")
    employee_id: Optional[UUID]= Field(None, alias="employeeId", description="UUID of the employee.")
    document_category_id: Optional[UUID] = Field(None, alias="documentCatagoryId", description="UUID of the document catagory.")
    created_since: Optional[UUID] = Field(None,alias="createdSince",description="Documents created since this date")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = {"populate_by_name": True}

class GetEmploymentDocumentCatagories(BaseModel):
    company_id: UUID = Field(None,alias="companyId",description="UUID of the company")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = {"populate_by_name": True}

class EmptyScheduleModel(BaseModel):
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    employee_id: UUID = Field(..., alias="employeeId", description="UUID of the employee.")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Start date of the empty schedule period. Nullable.")
    id: Optional[UUID] = Field(None, description="UUID of the empty schedule record.")
    time_group_id: UUID = Field(..., alias="timeGroupId", description="UUID of the time group associated with the empty schedule.")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="End date of the empty schedule period. Nullable.")
    model_config = {"populate_by_name": True}

class GetEmploymentEmptySchedules(BaseModel):
    company_number: Optional[int] = Field(None, alias="companynumber", description="Company number.")
    employee_id: Optional[UUID] = Field(None, alias="employeeId", description="Employee ID (UUID).")
    employment_number: Optional[str] = Field(None, alias="employmentnumber", description="Employment number.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = {"populate_by_name": True}

class TravelRuleSetModel(BaseModel):
    allowance_according_to: Optional[int] = Field(None, alias="allowanceAccordingTo", description="Determines allowance rules source. 0 = Company, 1 = Employment.")
    allowance_rule_set_id: Optional[UUID] = Field(None, alias="allowanceRuleSetId", description="UUID of the allowance rule set. Nullable.")
    allow_selection_rule_set: Optional[bool] = Field(None, alias="allowSelectionRuleSet", description="Whether the employee can select their own rule set.")
    travel_time_according_to: Optional[int] = Field(None, alias="travelTimeAccordingTo", description="Determines travel time rules source. 0 = Company, 1 = Employment.")
    travel_time_rule_set_id: Optional[UUID] = Field(None, alias="travelTimeRuleSetId", description="UUID of the travel time rule set. Nullable.")
    use_trip_on_invoice: Optional[bool] = Field(None, alias="useTripOnInvoice", description="Whether to use trip on invoice.")
    model_config = {"populate_by_name": True}

class EmploymentPeriodModel(BaseModel):
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    create_payroll_transactions: Optional[bool] = Field(None, alias="createPayrollTransactions", description="Whether to automatically create payroll transactions for this employment period.")
    employee_id: UUID = Field(..., alias="employeeId", description="UUID of the employee.")
    employment_type_id: Optional[UUID] = Field(None, alias="employmentTypeId", description="UUID of the employment type. Nullable.")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Start date of the employment period. Nullable.")
    has_final_salary: Optional[bool] = Field(None, alias="hasFinalSalary", description="Whether the employment period has a final salary.")
    id: Optional[UUID] = Field(None, description="UUID of the employment period record.")
    instance_id: UUID = Field(..., alias="instanceId", description="UUID of the instance.")
    payment_group_id: Optional[UUID] = Field(None, alias="paymentGroupId", description="UUID of the payment group. Nullable.")
    resignation_cause_id: Optional[UUID] = Field(None, alias="resignationCauseId", description="UUID of the resignation cause. Nullable.")
    salary_type: Optional[int] = Field(None, alias="salaryType", description="Salary type. 0 = Monthly, 1 = Hourly, 2 = Yearly.")
    staff_category_id: Optional[UUID] = Field(None, alias="staffCategoryId", description="UUID of the staff category. Nullable.")
    title_id: Optional[UUID] = Field(None, alias="titleId", description="UUID of the employee's title. Nullable.")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="End date of the employment period. Nullable.")
    travel_rule_set: Optional[TravelRuleSetModel] = Field(None, alias="travelRuleSet", description="Travel rule set settings for this employment period.")
    model_config = {"populate_by_name": True}

class CreateEmploymentPeriod(BaseModel):
    employementtemplate_id: UUID = Field(None,alias="employementtemplateId",description="Create employment period with use of employment template. If left empty then no template will be used.")
    prioritize_employment_template: bool = Field(False,alias="prioritizeEmploymenttemplate",description="Default false. Determines whether values from template or model will be prioritized. False - will ensure all values from model overrite template values.")
    model_config = {"populate_by_name": True}

class EmploymentPersonalScheduleModel(BaseModel):
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    employee_id: UUID = Field(..., alias="employeeId", description="UUID of the employee.")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Start date of the personal schedule. Nullable.")
    id: Optional[UUID] = Field(None, description="UUID of the employment personal schedule record.")
    instance_id: UUID = Field(..., alias="instanceId", description="UUID of the instance.")
    personal_schedule_id: UUID = Field(..., alias="personalScheduleId", description="UUID of the personal schedule.")
    time_group_id: UUID = Field(..., alias="timeGroupId", description="UUID of the time group associated with the personal schedule.")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="End date of the personal schedule. Nullable.")
    model_config = {"populate_by_name": True}

class EmploymentPublicScheduleModel(BaseModel):
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    employee_id: UUID = Field(..., alias="employeeId", description="UUID of the employee.")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Start date of the public schedule. Nullable.")
    id: Optional[UUID] = Field(None, description="UUID of the employment public schedule record.")
    instance_id: UUID = Field(..., alias="instanceId", description="UUID of the instance.")
    public_schedule_id: UUID = Field(..., alias="publicScheduleId", description="UUID of the public schedule.")
    time_group_id: UUID = Field(..., alias="timeGroupId", description="UUID of the time group associated with the public schedule.")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="End date of the public schedule. Nullable.")
    model_config = {"populate_by_name": True}

class GetPublicEmploymentSchedules(GenericGetModel):
    include_empty_schedules: Optional[bool] = Field(True, alias="includeEmptySchedules", description="Whether to include empty schedules in the response. Nullable. Default: True")


class EmploymentRateModel(BaseModel):
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    employee_id: UUID = Field(..., alias="employeeId", description="UUID of the employee.")
    employment_rate_percent: Optional[float] = Field(None, alias="employmentRatePercent", description="Employment rate as a percentage of full time.")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Start date of the employment rate period. Nullable.")
    hours_per_full_time_work_week: Optional[float] = Field(None, alias="hoursPerFullTimeWorkWeek", description="Number of hours per week for a full time employee.")
    hours_per_full_time_work_year: Optional[float] = Field(None, alias="hoursPerFullTimeWorkYear", description="Number of hours per year for a full time employee.")
    id: Optional[UUID] = Field(None, description="UUID of the employment rate record.")
    instance_id: UUID = Field(..., alias="instanceId", description="UUID of the instance.")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="End date of the employment rate period. Nullable.")
    model_config = {"populate_by_name": True}

class GetEmplploymentTitles(BaseModel):
    instance: Optional[str] = Field(None, description="Domain name.")
    company_id: Optional[UUID] = Field(None, alias="companyId", description="Company ID (UUID).")
    company_number: Optional[int] = Field(None, alias="companynumber", description="Company number.")
    active: Optional[bool] = Field(None, description="Whether the employment title is active. Nullable.")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")
    model_config = {"populate_by_name": True}

class EmploymentTitleModel(BaseModel):
    active: Optional[bool] = Field(None, description="Whether the employment title is active. Nullable.")
    code: str = Field(..., min_length=1, description="Unique code for the employment title. Minimum length: 1.")
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    description: Optional[str] = Field(None, description="Description of the employment title. Nullable.")
    id: Optional[UUID] = Field(None, description="UUID of the employment title record.")
    instance_id: Optional[UUID] = Field(None, alias="instanceId", description="UUID of the instance.")
    name: str = Field(..., min_length=1, description="Name of the employment title. Minimum length: 1.")
    model_config = {"populate_by_name": True}

class GetEmploymentTypes(BaseModel):
    instance: Optional[str] = Field(None, description="Domain name.")
    company_id: Optional[UUID] = Field(None, alias="companyId", description="Company ID (UUID).")
    company_number: Optional[int] = Field(None, alias="companynumber", description="Company number.")
    page_params: Optional[PageModel] = Field(PageModel(),description="Page parameters")
    model_config = {"populate_by_name": True}

class VacationBalanceModel(BaseModel):
    ingoing: Optional[float] = Field(None, description="Ingoing vacation balance at the start of the vacation year.")
    remaining: Optional[float] = Field(None, description="Remaining vacation balance.")
    withdrawn: Optional[float] = Field(None, description="Withdrawn vacation balance.")
    model_config = {"populate_by_name": True}

class EmploymentVacationModel(BaseModel):
    advance_vacation_balance: Optional[VacationBalanceModel] = Field(None, alias="advanceVacationBalance", description="Balance details for advance vacation days.")
    company_id: Optional[UUID] = Field(None, alias="companyId", description="UUID of the company.")
    current_vacation_year: Optional[datetime] = Field(None, alias="currentVacationYear", description="Start date of the current vacation year.")
    daily_vacation_addition: Optional[float] = Field(None, alias="dailyVacationAddition", description="Daily vacation addition amount. Nullable.")
    daily_vacation_pay: Optional[float] = Field(None, alias="dailyVacationPay", description="Daily vacation pay amount. Nullable.")
    employee_id: Optional[UUID] = Field(None, alias="employeeId", description="UUID of the employee.")
    id: Optional[UUID] = Field(None, description="UUID of the employment vacation record.")
    instance_id: Optional[UUID] = Field(None, alias="instanceId", description="UUID of the instance.")
    paid_vacation_balance: Optional[VacationBalanceModel] = Field(None, alias="paidVacationBalance", description="Balance details for paid vacation days.")
    saved_vacation_balance: Optional[VacationBalanceModel] = Field(None, alias="savedVacationBalance", description="Balance details for saved vacation days.")
    unpaid_vacation_balance: Optional[VacationBalanceModel] = Field(None, alias="unpaidVacationBalance", description="Balance details for unpaid vacation days.")
    vacation_addition_variable: Optional[float] = Field(None, alias="vacationAdditionVariable", description="Variable vacation addition amount.")
    vacation_employment_rate: Optional[float] = Field(None, alias="vacationEmploymentRate", description="Employment rate used for vacation calculations.")
    model_config = {"populate_by_name": True}

class EmploymentVehicleModel(BaseModel):
    avg_price_per_liter: Optional[float] = Field(None, alias="avgPricePerLiter", description="Average price per liter of fuel. Nullable.")
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    consumption: Optional[float] = Field(None, description="Fuel consumption of the vehicle. Nullable.")
    employee_id: UUID = Field(..., alias="employeeId", description="UUID of the employee.")
    fuel_benefit: Optional[bool] = Field(None, alias="fuelBenefit", description="Whether the employee has a fuel benefit for this vehicle.")
    id: Optional[UUID] = Field(None, description="UUID of the employment vehicle record.")
    odometer_reading: Optional[float] = Field(None, alias="odometerReading", description="Current odometer reading of the vehicle. Nullable.")
    register_odometer_reading: Optional[bool] = Field(None, alias="registerOdometerReading", description="Whether to register odometer readings for this vehicle.")
    reg_number: Optional[str] = Field(None, alias="regNumber", description="Vehicle registration number. Nullable.")
    trip_log_from: Optional[datetime] = Field(None, alias="tripLogFrom", description="Start date for trip log recording. Nullable.")
    trip_log_to: Optional[datetime] = Field(None, alias="tripLogTo", description="End date for trip log recording. Nullable.")
    vehicle_type: UUID = Field(..., alias="vehicleType", description="UUID of the vehicle type.")
    model_config = {"populate_by_name": True}

class GetEmploymentVehicles(BaseModel):
    employee_id: Optional[UUID] = Field(None, alias="employeeId", description="UUID of the employee.")
    vechile_type: Optional[UUID] = Field(None, alias="vechileType", description="UUID of the vehicle type.")
    trip_log_from: Optional[datetime] = Field(None, alias="tripLogFrom", description="Start date for filtering employment vehicles based on trip log recording.")
    trip_log_to: Optional[datetime] = Field(None, alias="tripLogTo", description="End date for filtering employment vehicles based on trip log recording.")
    reg_nummber: Optional[str] = Field(None, alias="regNumber", description="Vehicle registration number for filtering employment vehicles.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = {"populate_by_name": True}

class HrFormDecimalSettingModel(BaseModel):
    id: Optional[UUID] = Field(None, description="UUID of the decimal setting record.")
    rounding_policy: Optional[int] = Field(None, alias="roundingPolicy", description="Rounding policy for decimal values. 0 = None, 1 = Up, 2 = Down, 3 = NearestInteger.")
    type: Optional[int] = Field(None, description="Type of decimal setting. 0 = MonthlySalary, 1 = HourlySalary, 2 = AnnualSalary, 3 = ContractualWorkingHours, 4 = WorkingHoursHoursPerWeekActual, 5 = WorkingHoursHoursPerWeekFullTime, 6 = WorkingHoursPerYearActual, 7 = WorkingHoursPerYearFullTime.")
    model_config = {"populate_by_name": True}


class HttpFileModel(BaseModel):
    content_length: Optional[int] = Field(None, alias="contentLength", description="Length of the file content in bytes.")
    content_type: Optional[str] = Field(None, alias="contentType", description="MIME type of the file. Nullable.")
    file_content: Optional[str] = Field(None, alias="fileContent", description="Base64 encoded file content. Nullable.")
    file_name: Optional[str] = Field(None, alias="fileName", description="Name of the file. Nullable.")
    model_config = {"populate_by_name": True}


class HrFormModel(BaseModel):
    allow_edit_when_e_signing: Optional[bool] = Field(None, alias="allowEditWhenESigning", description="Whether the form can be edited during e-signing.")
    can_be_chosen_as_attachment: Optional[bool] = Field(None, alias="canBeChosenAsAttachment", description="Whether the form can be chosen as an attachment.")
    can_be_saved_directly_to_employee_document: Optional[bool] = Field(None, alias="canBeSavedDirectlyToEmployeeDocument", description="Whether the form can be saved directly to employee documents.")
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    decimal_settings: Optional[list[HrFormDecimalSettingModel]] = Field(None, alias="decimalSettings", description="List of decimal settings for the HR form. Nullable.")
    description: Optional[str] = Field(None, description="Description of the HR form. Nullable.")
    disable_manual_editing: Optional[bool] = Field(None, alias="disableManualEditing", description="Whether manual editing of the form is disabled.")
    document_format_download_options: Optional[int] = Field(None, alias="documentFormatDownloadOptions", description="Available download formats. 0 = DOCX, 1 = PDF, 2 = All.")
    employment_document_category_id: Optional[UUID] = Field(None, alias="employmentDocumentCategoryId", description="UUID of the employment document category. Nullable.")
    e_signing: Optional[bool] = Field(None, alias="eSigning", description="Whether e-signing is enabled for this form.")
    file: Optional[HttpFileModel] = Field(None, description="File associated with the HR form.")
    filter_step: Optional[bool] = Field(None, alias="filterStep", description="Whether the filter step is enabled for this form.")
    hr_form_rule_for_date_controller_values: Optional[int] = Field(None, alias="hrFormRuleForDateControllerValues", description="Rule for date controller values. 0 = EmploymentPeriodStartDate, 1 = CurrentValue, 2 = EmploymentPeriodSelectedValue.")
    id: Optional[UUID] = Field(None, description="UUID of the HR form record.")
    is_active: Optional[bool] = Field(None, alias="isActive", description="Whether the HR form is active.")
    name: Optional[str] = Field(None, description="Name of the HR form. Nullable.")
    type: Optional[int] = Field(None, description="Type of HR form. 0 = HrForm, 1 = Resume, 2 = All, 3 = EmploymentContract, 4 = StartPage.")
    model_config = {"populate_by_name": True}

class GetHrForms(BaseModel):
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    comany_number: Optional[int] = Field(None, alias="companynumber", description="Company number.")
    hr_form_type: Optional[int] = Field(None, alias="hrFormType", description="Type of HR form to filter by. 0 = HrForm, 1 = Resume, 2 = All, 3 = EmploymentContract, 4 = StartPage.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = {"populate_by_name": True}

class NewCompanyViewModel(BaseModel):
    company_name: str = Field(..., alias="companyName", min_length=1, description="Name of the new company. Minimum length: 1.")
    company_number: int = Field(..., alias="companyNumber", description="Company number for the new company.")
    company_number_to_copy_from: Optional[int] = Field(None, alias="companyNumberToCopyFrom", description="Company number of the existing company to copy settings from.")
    copy_settings_from_existing_company: bool = Field(..., alias="copySettingsFromExistingCompany", description="Whether to copy settings from an existing company.")
    country_code: Optional[str] = Field(None, alias="countryCode", description="Country code for the new company. Nullable.")
    culture: Optional[str] = Field(None, description="Culture/locale setting for the new company. Nullable.")
    currency_code: Optional[str] = Field(None, alias="currencyCode", description="Currency code for the new company.")
    customer_instance_domain: str = Field(DOMAIN, alias="customerInstanceDomain", min_length=1, description="Instance domain for the new company. Minimum length: 1.")
    customer_instance_domain_to_copy_from: Optional[str] = Field(None, alias="customerInstanceDomainToCopyFrom", description="Instance domain of the existing company to copy settings from. Nullable.")
    include_roles_when_copying_between_instances: Optional[bool] = Field(None, alias="includeRolesWhenCopyingBetweenInstances", description="Whether to include roles when copying settings between instances.")
    organization_number: Optional[str] = Field(None, alias="organizationNumber", description="Organization registration number for the new company. Nullable.")
    model_config = {"populate_by_name": True}

class GetImportedTripsByEmployeeId(BaseModel):
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    sort_order: Optional[int] = Field(0, alias="sortOrder", description="The order of the list sorted by the column FromDateTime. Defaults to ascending.0 = Ascending, 1 = Descending, -1 = Unspecified.")
    from_start_date: Optional[datetime] = Field(None, alias="fromStartDate", description="Filter that the start date is from. Format YYYY-MM-DD. Defaults to null")
    to_start_date: Optional[datetime] = Field(None, alias="toStartDate", description="Filter that the start date is to. Format YYYY-MM-DD. Defaults to null")
    show_deleted: Optional[bool] = Field(True, alias="showDeleted", description="Whether to include deleted trips in the results. Defaults to True.")
    show_reconciled: Optional[bool] = Field(True, alias="showReconciled", description="Whether to include reconciled trips in the results. Defaults to True.")
    show_non_reconciled: Optional[bool] = Field(True, alias="showNonReconciled", description="Whether to include non-reconciled trips in the results. Defaults to True.")
    model_config = {"populate_by_name": True}

class ImportedTripModel(BaseModel):
    comment: Optional[str] = Field(None, description="Comment for the trip. Nullable.")
    distance: Optional[float] = Field(None, description="Distance of the trip. Nullable.")
    employee_id: UUID = Field(..., alias="employeeId", description="UUID of the employee.")
    from_date_time: datetime = Field(..., alias="fromDateTime", description="Start date and time of the trip.")
    from_mileage: Optional[float] = Field(None, alias="fromMileage", description="Odometer reading at the start of the trip. Nullable.")
    from_street: Optional[str] = Field(None, alias="fromStreet", description="Street address at the start of the trip. Nullable.")
    id: Optional[UUID] = Field(None, description="UUID of the imported trip record.")
    license_plate: Optional[str] = Field(None, alias="licensePlate", description="License plate of the vehicle used for the trip. Nullable.")
    to_date_time: datetime = Field(..., alias="toDateTime", description="End date and time of the trip.")
    to_mileage: Optional[float] = Field(None, alias="toMileage", description="Odometer reading at the end of the trip. Nullable.")
    to_street: Optional[str] = Field(None, alias="toStreet", description="Street address at the end of the trip. Nullable.")
    model_config = {"populate_by_name": True}

class NextOfKinModel(BaseModel):
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    contact_info: Optional[str] = Field(None, alias="contactInfo", description="Contact information for the next of kin. Nullable.")
    employee_id: UUID = Field(..., alias="employeeId", description="UUID of the employee.")
    id: Optional[UUID] = Field(None, description="UUID of the next of kin record.")
    informed: Optional[bool] = Field(None, description="Whether the next of kin has been informed.")
    instance_id: UUID = Field(..., alias="instanceId", description="UUID of the instance.")
    name: Optional[str] = Field(None, description="Name of the next of kin. Nullable.")
    relation: str = Field(..., min_length=1, description="Relation of the next of kin to the employee. Minimum length: 1.")
    model_config = {"populate_by_name": True}

class GetOwnFieldModel(BaseModel):
    instance: Optional[str] = Field(None, description="Domain name.")
    company_id: Optional[UUID] = Field(None, alias="companyId", description="Company ID (UUID).")
    company_number: Optional[int] = Field(None, alias="companynumber", description="Company number.")
    side_element: Optional[int] = Field(None, alias="sideElement", description="Type of page element. 0 = FieldGroupWithDateHistory, 1 = FormTemplate, 2 = StaffAppraisal, 3 = HeadlineLevelOne, 4 = HeadlineLevelTwo, 5 = FieldGroupWithoutDateHistory, 6 = Table.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = {"populate_by_name": True}

class OwnAssessmentFieldValueModel(BaseModel):
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    employee_id: UUID = Field(..., alias="employeeId", description="UUID of the employee.")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Start date of the own assessment field value validity period. Nullable.")
    id: Optional[UUID] = Field(None, description="UUID of the own assessment field value record.")
    instance_id: UUID = Field(..., alias="instanceId", description="UUID of the instance.")
    own_assessment_field_id: UUID = Field(..., alias="ownAssessmentFieldId", description="UUID of the own assessment field this value belongs to.")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="End date of the own assessment field value validity period. Nullable.")
    value: Optional[float] = Field(None, description="The assessment field value.")
    model_config = {"populate_by_name": True}

class OwnDateFieldValueModel(BaseModel):
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    employee_id: UUID = Field(..., alias="employeeId", description="UUID of the employee.")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Start date of the own date field value validity period. Nullable.")
    id: Optional[UUID] = Field(None, description="UUID of the own date field value record.")
    instance_id: UUID = Field(..., alias="instanceId", description="UUID of the instance.")
    own_date_field_id: UUID = Field(..., alias="ownDateFieldId", description="UUID of the own date field this value belongs to.")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="End date of the own date field value validity period. Nullable.")
    model_config = {"populate_by_name": True}

class OwnNumericalFieldValueModel(BaseModel):
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    employee_id: UUID = Field(..., alias="employeeId", description="UUID of the employee.")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Start date of the own numerical field value validity period. Nullable.")
    id: Optional[UUID] = Field(None, description="UUID of the own numerical field value record.")
    instance_id: UUID = Field(..., alias="instanceId", description="UUID of the instance.")
    own_numerical_field_id: UUID = Field(..., alias="ownNumericalFieldId", description="UUID of the own numerical field this value belongs to.")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="End date of the own numerical field value validity period. Nullable.")
    value: Optional[float] = Field(None, description="The numerical field value.")
    model_config = {"populate_by_name": True}

class OwnTextFieldValueModel(BaseModel):
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    employee_id: UUID = Field(..., alias="employeeId", description="UUID of the employee.")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Start date of the own text field value validity period. Nullable.")
    id: Optional[UUID] = Field(None, description="UUID of the own text field value record.")
    instance_id: UUID = Field(..., alias="instanceId", description="UUID of the instance.")
    own_text_field_id: UUID = Field(..., alias="ownTextFieldId", description="UUID of the own text field this value belongs to.")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="End date of the own text field value validity period. Nullable.")
    value: Optional[str] = Field(None, description="The text field value.")
    model_config = {"populate_by_name": True}

class GetPaycodesWithStaffCategorySettings(BaseModel):
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    staff_category_id: UUID = Field(..., alias="staffCategoryId", description="UUID of the staff category.")
    last_modified: Optional[datetime] = Field(None, alias="lastModified", description="Filter pay codes that have been modified since this date. Nullable.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = {"populate_by_name": True}

class GetPaymentGroups(BaseModel):
    instance: Optional[str] = Field(None, description="Domain name.")
    company_id: Optional[UUID] = Field(None, alias="companyId", description="Company ID (UUID).")
    company_number: Optional[int] = Field(None, alias="companynumber", description="Company number.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = {"populate_by_name": True}

class GetPayrollRuns(BaseModel):
    compamny_id: Optional[UUID] = Field(None, alias="companyId", description="Company ID (UUID).")
    payroll_run_number: Optional[str] = Field(None, alias="payrollRunNumber", description="Payroll run number.")
    payment_group_id: Optional[UUID] = Field(None, alias="paymentGroupId", description="Payment group ID (UUID).")
    status: Optional[int] = Field(None, description="Payroll run status 0 = Preliminary, 1 = Settled")
    payroll_run_type: Optional[int] = Field(None, alias="payrollRunType", description="Payroll run type. 0 = Ordinary, 1 = Extra")
    payment_date: Optional[datetime] = Field(None, alias="paymentDate", description="Date of payment")
    payroll_period_from: Optional[datetime] = Field(None, alias="payrollPeriodFrom", description="Start date of the payroll period.")
    payroll_period_to: Optional[datetime] = Field(None, alias="payrollPeriodTo", description="End date of the payroll period.")
    discrepency_period_from: Optional[datetime] = Field(None, alias="discrepencyPeriodFrom", description="Start date of the discrepancy period.")
    discrepency_period_to: Optional[datetime] = Field(None, alias="discrepencyPeriodTo", description="End date of the discrepancy period.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = {"populate_by_name": True}

class GetPayrollRunEmployments(BaseModel):
    company_id: Optional[UUID] = Field(None, alias="companyId", description="Company ID (UUID).")
    payroll_run_id: Optional[UUID] = Field(None, alias="payrollRunId", description="Payroll run ID (UUID).")
    empployee_id: Optional[UUID] = Field(None, alias="employeeId", description="Employee ID (UUID).")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = {"populate_by_name": True}

class GetPayrollRunTransactions(BaseModel):
    company_id: Optional[UUID] = Field(None, alias="companyId", description="Company ID (UUID).")
    payroll_run_id: Optional[UUID] = Field(None, alias="payrollRunId", description="Payroll run ID (UUID).")
    payroll_run_employee_id: Optional[UUID] = Field(None, alias="payrollRunEmployeeId", description="Payroll run employee ID (UUID).")
    employee_id: Optional[UUID] = Field(None, alias="employeeId", description="Employee ID (UUID).")
    paycode_id: Optional[UUID] = Field(None, alias="paycodeId", description="Pay code ID (UUID).")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = {"populate_by_name": True}

class GetPayrollRunTransactionAccountCollections(BaseModel):
    company_id: Optional[UUID] = Field(None, alias="companyId", description="Company ID (UUID).")
    payroll_run_id: Optional[UUID] = Field(None, alias="payrollRunId", description="Payroll run ID (UUID).")
    payroll_run_employee_id: Optional[UUID] = Field(None, alias="payrollRunEmployeeId", description="Payroll run employee ID (UUID).")
    payroll_run_transaction_id: Optional[UUID] = Field(None, alias="payrollRunTransactionId", description="Payroll run transaction ID (UUID).")
    paycode_id: Optional[UUID] = Field(None, alias="paycodeId", description="Pay code ID (UUID).")
    employee_id: Optional[UUID] = Field(None, alias="employeeId", description="Employee ID (UUID).")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = {"populate_by_name": True}

class AgreementAreaModel(BaseModel):
    anstallningskategori: Optional[int] = Field(None, description="Employment category. 0 = Ovriga, 1 = A, 2 = B, 3 = C, 4 = D, 5 = E, 6 = F, 7 = G, 8 = H, 9 = J, 10 = K, 11 = L, 12 = M, 13 = N, 14 = O, 15 = P, 16 = R, 17 = S, 18 = T, 19 = V, 20 = Y, 21 = Z.")
    employment_option_spv: Optional[int] = Field(None, alias="employmentOptionSpv", description="SPV employment type. 0 = H1, 1 = H3, 2 = T8.")
    employment_pension_and_insurance_id: Optional[UUID] = Field(None, alias="employmentPensionAndInsuranceId", description="UUID of the employment pension and insurance record.")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Start date of the agreement area validity period. Nullable.")
    organizational_home: Optional[str] = Field(None, alias="organizationalHome", description="Organizational home for the agreement area. Nullable.")
    pension_agreement: Optional[int] = Field(None, alias="pensionAgreement", description="Pension agreement affiliation. 0 = Inget, 1 = Avdelning1, 2 = Avdelning2.")
    retirement_age: Optional[int] = Field(None, alias="retirementAge", description="Retirement age for this agreement area. Nullable.")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="End date of the agreement area validity period. Nullable.")
    model_config = {"populate_by_name": True}

class MarkupCodeModel(BaseModel):
    code: Optional[int] = Field(None, description="Markup code. 0 = Teknikavtalet, 1 = TEKOavtalet, 2 = Livsmedelsavtalet, 3 = Tobaksavtalet, 4 = AvtaletForVinOchSpritindustrin, 5 = KafferosterierOchKryddfabriker, 6 = Byggnadsamnesindustrin, 7 = Buteljglasindustrin, 8 = Motorbranschavtalet, 9 = Industriavtalet, 10 = KemiskaFabriker, 11 = Glasindustrin, 12 = GemensammaMetall, 13 = Explosivamnesindustrin, 14 = IAvtalet, 15 = AllokemiskaIndustrin, 16 = InStenindustringen, 17 = LaderOchSportartiklar, 18 = Atervinningsforetag, 19 = Tvattindustrin, 20 = Oljeraffinaderier, 21 = Sockerindustrin, 22 = IMGavtalet, 23 = Sagverksavtalet, 24 = Skogsbruk, 25 = Virkesmatning, 26 = Stoppmobelindustrin, 27 = Traindustri, 28 = Infomediaavtalet, 29 = Forpackningsavtalet, 30 = AhlsellGeliaSvFoderTeknosam, 31 = HandelOchMetallAvtalet, 32 = Studsviksavtalet, 33 = FlygteknikerMedTypcertifikat, 34 = MassaOchPappersindustrin, 35 = StalOchMetallindustrinBlaAvtalet, 36 = Tidningsavtalet, 37 = Maleriyrket, 38 = Installationsavtalet, 39 = Kraftverksavtalet, 40 = Elektroskandiaavtalet, 41 = Bemanningsforetag, 42 = Byggavtalet, 43 = DalslandsKanal, 44 = Detaljhandeln, 45 = Entreprenadmaskinavtalet, 46 = Glasmasteriavtalet, 47 = GotaKanalbolagAB, 48 = Lageravtalet, 49 = LagerOchEhandelsavtalet, 50 = LagerpersonalVidGlassforetag, 51 = LarmOchSakerhetsteknikavtalet, 52 = Maskinforaravtalet, 53 = PlatOchVentilationsavtalet, 54 = Privatteateravtalet, 55 = Stadavtalet, 56 = TeknikinstallationVVSOchKyl, 57 = RestaurangOchCafeAnstallda, 58 = SkargardstrafikASL, 59 = Vardepapper, 60 = VagOchBanavtalet, 61 = TRIASkolaochVard, 62 = STANLEYSecurity, 63 = Danscentrumavtalet, 64 = Teatercentrumavtalet, 65 = KollektivavtaletRadioTVDataElektrotekniker, 66 = Spårtrafik, 67 = Gruventreprenadavtalet, 68 = Trävaruhandelsavtalet.")
    employment_pension_and_insurance_id: Optional[UUID] = Field(None, alias="employmentPensionAndInsuranceId", description="UUID of the employment pension and insurance record.")
    from_date: Optional[datetime] = Field(None, alias="fromDate", description="Start date of the markup code validity period. Nullable.")
    to_date: Optional[datetime] = Field(None, alias="toDate", description="End date of the markup code validity period. Nullable.")
    model_config = {"populate_by_name": True}

class PensionAndInsuranceModel(BaseModel):
    agreement_areas: Optional[list[AgreementAreaModel]] = Field(None, alias="agreementAreas", description="List of agreement areas for this pension and insurance record. Nullable.")
    category: Optional[int] = Field(None, description="Pension and insurance category. 0 = RedovisaEjTillFora, 1 = Arbetare, 2 = Tjansteman, 3 = TjanstemanAnstalldVD.")
    contractual_pension_after_65: Optional[bool] = Field(None, alias="contractualPensionAfter65", description="Whether the employee has contractual pension after age 65.")
    cost_center: Optional[int] = Field(None, alias="costCenter", description="Cost center number. Nullable.")
    has_occupational_pension_account_at_spv: Optional[bool] = Field(None, alias="hasOccupationalPensionAccountAtSpv", description="Whether the employee has an occupational pension account at SPV.")
    kpa_allocation_over_limit_percent: Optional[float] = Field(None, alias="kpaAllocationOverLimitPercent", description="KPA allocation percentage over the limit. Nullable.")
    kpa_allocation_under_limit_percent: Optional[float] = Field(None, alias="kpaAllocationUnderLimitPercent", description="KPA allocation percentage under the limit. Nullable.")
    kpa_management_number: Optional[str] = Field(None, alias="kpaManagementNumber", description="KPA management number. Nullable.")
    kpa_pension_plan_type: Optional[int] = Field(None, alias="kpaPensionPlanType", description="KPA pension plan type. 0 = Inget, 6 = KapKl, 13 = AkapKr.")
    markup_codes: Optional[list[MarkupCodeModel]] = Field(None, alias="markupCodes", description="List of markup codes for this pension and insurance record. Nullable.")
    pension_plan_id: Optional[str] = Field(None, alias="pensionPlanId", description="Pension plan ID. Nullable.")
    pension_plan_type: Optional[int] = Field(None, alias="pensionPlanType", description="Pension plan type. a number where 0 = nothing, 1 = ITP1, 2 = ITP2 WorkingIncapacity is a number in string format and represents the percent of working incapacity. The following strings can be registred: 0, 25, 50, 75.")
    person_id: Optional[UUID] = Field(None, alias="personId", description="UUID of the person associated with this pension and insurance record.")
    working_incapacity: Optional[str] = Field(None, alias="workingIncapacity", description="Working incapacity information for the employee. Nullable.")
    model_config = {"populate_by_name": True}

class GetPensionAndInsuranceSettings(BaseModel):
    companynumber: Optional[int] = Field(None, alias="companynumber", description="Company number.")
    employmentnumber: Optional[str] = Field(None, alias="employeeNumber", description="Employment number.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = {"populate_by_name": True}

class GetEmployeePresenceByCompany(BaseModel):
    company_id: UUID = Field(..., alias="companyId", description="UUID of the company.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = {"populate_by_name": True}

class PresenceSelectionFilterModel(BaseModel):
    employees: Optional[list[UUID]] = Field(None, description="List of employee UUIDs to filter by. Nullable.")
    employment_default_accounts: Optional[list[UUID]] = Field(None, alias="employmentDefaultAccounts", description="List of employment default account UUIDs to filter by. Nullable.")
    presence_sort_column_type: Optional[int] = Field(None, alias="presenceSortColumnType", description="Column to sort presence by. 0 = Status, 1 = InOut, 2 = Employee, 3 = Firstname, 4 = Lastname, 5 = Company.")
    presence_status_type: Optional[int] = Field(None, alias="presenceStatusType", description="Filter by presence status. 0 = All, 1 = In, 2 = Out.")
    registered_on_accounts: Optional[list[UUID]] = Field(None, alias="registeredOnAccounts", description="List of account UUIDs to filter presence registrations by. Nullable.")
    show_only_scheduled: Optional[bool] = Field(None, alias="showOnlyScheduled", description="Whether to show only scheduled employees.")
    sort_order: Optional[int] = Field(None, alias="sortOrder", description="Sort order. 0 = Ascending, 1 = Descending, -1 = Unspecified.")
    time_groups: Optional[list[UUID]] = Field(None, alias="timeGroups", description="List of time group UUIDs to filter by. Nullable.")

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
    active_to_date: Optional[datetime] = Field(None, alias="activeTomDate", description="Date until which the project is active.")
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
    billing: Optional[AccountBillingModel] = Field(None, description="Billing configuration for this project.")
    project_time_report_controls: Optional[list[ProjectTimeReportControl]] = Field(
        None,
        alias="projectTimeReportControls",
        description="Time report controls (warnings/errors) applied to this project."
    )
    work_place: Optional[WorkplaceModel] = Field(None, alias="workPlace", description="Workplace associated with this project.")
 
    model_config = {"populate_by_name": True}

class GetReportedHoursOnProjects(BaseModel):
    account_distribution_id: UUID = Field(..., alias="accountDistributionId", description="Reported hours will be fetched for projects under selected AccountDistribution")
    status: int = Field(..., description="Will report hours of projects with selected Projectstatus. 0 = Ongoing, 1 = Frozen, 2 = Ended")
    from_date: datetime = Field(None, alias="fromDate", description="Filter for reported hours from this date (inclusive).")
    to_date: datetime = Field(None, alias="toDate", description="Filter for reported hours to this date (inclusive).")
    project_id: Optional[UUID] = Field(None, alias="projectId", description="Filter for reported hours on a specific project. Nullable. If not set, all projects will be calculated")
    include_employments: Optional[bool] = Field(False, alias="includeEmployments", description="If set to true then summary will include ReportedProjectEmployments. Default value is false.")
    include_allowances: Optional[bool] = Field(False, alias="includeAllowances", description="If set to true then summary will include allowances (of type timecode). Will increase response time considerably. Default value is false.")
    include_undefines_time_codes: Optional[bool] = Field(False, alias="includeUndefinedTimeCodes", description="If set to true then summary will also include rows with timecodes that have code type undefined. Default value is false and will only include code type attendance.")
    hide_projects_with_no_reported_hours: Optional[bool] = Field(False, alias="hideProjectsWithNoReportedHours", description="If set to true then projects with no reported hours will be filtered out from the response. Default value is false.")
    model_config = {"populate_by_name": True}

class GetProjects(BaseModel):
    company: str = Field(..., description="Company number.")
    instance: str = Field(INSTANCE, description="Domain name.")
    code: Optional[str] = Field(None, description="Project code to filter by.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    modified_since: Optional[datetime] = Field(None, alias="modifiedSince", description="Get projects that have been created or modified from this date and time. YYYY-MM-DDTHH:MM:SS.")
    model_config = {"populate_by_name": True}

class GetPublicSchedule(BaseModel):
    instance: Optional[str] = Field(INSTANCE, description="Domain name.")
    company_id: Optional[UUID] = Field(None, alias="companyId", description="Company ID (UUID).")
    companynumber: Optional[int] = Field(None, alias="companyNumber", description="Company number.")
    page_params: Optional[PageModel] = Field(PageModel(), description="Page parameters")
    model_config = {"populate_by_name": True}

class GetTravelClaims(BaseModel):
    instance: Optional[str] = Field(INSTANCE,description="Domain name.")
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
 
 
class ProjectTimeReportControl(BaseModel):
    limit: float = Field(None,description="The threshold value for the control.")
    summary: int = Field(None,description="Control summary scope. 0 = Hierarchic, 1 = Individual.")
    type: int = Field(None,description="Control type. 0 = Warning, 1 = Error.")
 
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





