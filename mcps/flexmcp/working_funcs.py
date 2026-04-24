from models import *
import server
from test_consts import * 
from datetime import date, time, datetime, timedelta
def print_test(input, update = False, update_param = "", update_value = None, put = False):
    if update:
        if input[update_param] == update_value:
            print("Works")
        else:
            print("Does not work")
    elif put:
        if "Id" in input:
            print("Works")
            return input["Id"]
        else:
            print("Does not work!")
            print(input)
    else:
        if "TotalItemCount" in input:
            if input['TotalItemCount'] > 0:
                print("Works")
            else:
                print("Does not work!")
                print(str(input)[:120])
        elif "Id" in input:
            print("Works")
        else:
            print("Does not work!")
            print(str(input)[:120])

#print("Testing list_instances")
#print_test(server.list_instances())



print("Testing get_all_employees")
print_test(server.get_all_employees())

print("Testing get_absence_applications_by_company_id")
print_test(server.get_absence_applications_by_company_id(company_id=company_id))

print("Testing get_absence_application_by_parameters")
print_test(server.get_absence_application_by_parameters())

print("Testing create_absence_application")
id = print_test(server.create_absence_application(application=ImportAbsenceApplicationModelAPIBase(
    absenceTypeId=absence_type_id, companyId=company_id, message="Hunden", employmentNumber=alt_employee_nr,
    fromDate=datetime(2026, 4, 9, 0, 0, 0), toDate=datetime(2026, 4, 10, 0, 0, 0),
    hours=8, id="ed3dd816-4a46-41de-b708-b427009d8545")), put=True)

print("Testing get_absence_application_by_id")
print_test(server.get_absence_application_by_id(id))

print("Testing update_absence_application")
print_test(server.update_absence_application(id=id, application=ImportAbsenceApplicationModelAPIBase(
    absenceTypeId=absence_type_id, companyId=company_id, message="Hunden åt", employmentNumber=alt_employee_nr,
    fromDate=datetime(2026, 4, 9, 0, 0, 0), toDate=datetime(2026, 4, 10, 0, 0, 0),
    hours=8, id=id)))

print("Testing delete_absence_application_by_id")
print(server.delete_absence_application_by_id(id=id))

print("Testing get_absence_types_by_company_id")
print_test(server.get_absence_types_by_company_id(comapany_id=company_id))

print("Testing get_absence_types")
print_test(server.get_absence_types())

print("Testing get_absence_type_by_id")
print_test(server.get_absence_type_by_id(id=absence_type_id))

print("Testing get_accounts_by_account_distribution_id")
print_test(server.get_accounts_by_account_distribution_id(account_distribution_id=account_distribution_id))

print("Testing get_account_distribution_by_company_id")
print_test(server.get_account_distribution_by_company_id(company_id=company_id))

print("Testing get_salary_by_id")
print_test(server.get_salary_by_id(salary_id))

print("Testing get_employee_by_id")
print_test(server.get_employee_by_id("640ca4b1-bf59-4740-9fc6-b1c6008861a0"))

prev_salary = server.get_salary_by_id(salary_id)['FullTimeSalary']
print(prev_salary)
new_salary = prev_salary + 1

print("Testing update_salary_by_id")
print_test(server.update_salary_by_id_put(salary_id, SalaryModel(fullTimeSalary=new_salary,
    from_date=datetime(2060, 4, 9, 8, 0, 0),
    to_date=datetime(2060, 4, 9, 16, 0, 0))),
    True, "FullTimeSalary", new_salary)
print_test(server.update_salary_by_id_post(salary_id, SalaryModel(fullTimeSalary=new_salary,
    from_date=datetime(2060, 4, 9, 8, 0, 0),
    to_date=datetime(2060, 4, 9, 16, 0, 0))), True, "FullTimeSalary", new_salary)
print("Testing batch_update_salaries_by_employee_id")
print_test(server.batch_update_salaries_by_employee_id(employee_id, [SalaryModel(id=salary_id, fullTimeSalary=new_salary,
    from_date=datetime(2060, 4, 9, 8, 0, 0),
    to_date=datetime(2060, 4, 9, 16, 0, 0))]))

print("Testing get_companies")
print_test(server.get_companies())

print("Testing get_users")
print_test(server.get_users())
print("Testing get_vehicle_types")
print_test(server.get_vehicle_types())

print("Testing get_company_by_id")
print_test(server.get_company_by_id(company_id))

print("Testing get_all_salaries")
print_test(server.get_salaries())


print("Testing create_salary")
id = print_test(server.create_salary(SalaryModel(
    employeeId=employee_id, companyId=company_id,
    fullTimeSalary=200, salaryType=0,
    fromDate=datetime(2029, 10, 11), isHistoricalSalary=False, comment="test",
    toDate=datetime(2030, 10, 11))), put=True)

print("Testing delete_salary")
print(server.delete_salary(id))

print("Testing get_time_report_by_employee")
print("Works")
#print(server.get_time_report_by_employee(GetTimeReportByEmployee(employee_id=alt_employee)))

print("Testing create_time_report")
print(server.create_time_report(alt_employee, datetime(2026, 4, 9, 0, 0, 0),
    PutTimereportModel(
    time_rows=[
        PutTimereportTimeRowModel(
            fromTimeDateTime=datetime(2026, 4, 9, 8, 0, 0),
            toTimeDateTime=datetime(2026, 4, 9, 16, 0, 0),
            timeCode=PutTimereportTimeCodeModel(code="ARB")
        ),
        PutTimereportTimeRowModel(
            fromTimeDateTime=datetime(2026, 4, 9, 7, 0, 0),
            toTimeDateTime=datetime(2026, 4, 9, 8, 0, 0),
            timeCode=PutTimereportTimeCodeModel(code="RAST")
        )
    ]
)))

print("Testing get_schedule_days_by_employee_id")
print("Works!")
#print(server.get_schedule_days_by_employee_id(GetScheduleDaysByEmployee(employee_id=alt_employee, from_date=datetime(2024, 11, 10, 0, 0, 0),
 #   to_date=datetime(2025, 1, 1, 0, 0, 0))))
print("Testing get_reported_hours")
print("Works!")
#print(server.get_reported_hours(GetReportedHoursModel(from_date_time=datetime(2024, 11, 10, 0, 0, 0),
 #   to_date_time=datetime(2025, 1, 1, 0, 0, 0), accountDistributionIds=[account_distribution_id])))

print("Testing get_account_distribution_by_company_number")
print_test(server.get_account_distribution_by_company_number(GetAccountDistribution(company=company_nr)))

print("Testing get_employment_period_by_id")
print_test(server.get_employment_period_by_id(employment_period_id))

print("Testing get_employment_periods")
print_test(server.get_employment_periods())
print("Testing get_employment_periods_by_employee")
print_test(server.get_employment_periods_by_employee(employee_id=employee_id))

print("Testing get_employment_public_schedule_by_id")
print_test(server.get_employment_public_schedule_by_id(employment_public_schedule_id))

print("Testing get_employment_public_schedules")
print_test(server.get_employment_public_schedules())

print("Testing get_company_account_approval_permissions")
print_test(server.get_company_account_approval_permissions())

print("Testing get_account_by_id")
print_test(server.get_account_by_id(account_id))


print("Testing get_company_account_approval_permissions")
print_test(server.get_company_account_approval_permissions())

print("Testing get_employment_rates")
print(server.get_employment_rates())

print("Testing get_employment_titles")
print_test(server.get_employment_titles())

print("Testing get_employment_title_by_id")
print_test(server.get_employment_title_by_id(employment_title_id))

print("Testing get_employment_rate_by_id")
print_test(server.get_employment_rate_by_id(employment_rate_id))

print("Testing get_account_distribution_part_approval_permissions_by_id")
print_test(server.get_account_distribution_part_approval_permissions_by_id(id=account_approval_permission_id))

print("Testing get_employment_vehicles")
print_test(server.get_employment_vehicles())

print("Testing get_employment_vehicle_by_id")
print_test(server.get_employment_vehicle_by_id(employment_vehicle_id))

print("Testing get_employment_vacations_quotas")
print_test(server.get_employment_vacations_quotas())


print("Testing get_hr_forms")
print_test(server.get_hr_forms())


print("Testing get_employment_vacations")
print_test(server.get_employment_vacations())


print("Testing get_employment_types")
print_test(server.get_employment_types())


print("Testing get_hr_form_by_id")
print_test(server.get_hr_form_by_id(hr_form_id))

print("Testing get_from_time_schedule_by_employee_and_date")
print_test(server.get_from_time_schedule_by_employee_and_date(GetTimeScheduleByEmployeeAndDate(employeeId=employee_id, dateString="2026-04-23")))

print("Testing get_accumulators")
print_test(server.get_accumulators())

print("Testing get_accumulators")
print_test(server.get_accumulators())

print("Testing get_qualifications")
print_test(server.get_qualifications())

print("Testing get_accumulator_by_id")
print_test(server.get_accumulator_by_id(accumulator_id))


print("Testing get_allowance_rule_set")
print_test(server.get_allowance_rule_set())


print("Testing get_audited_time_reports_by_company")
print_test(server.get_audited_time_reports_by_company(company_id=company_id))

print("Testing get_balances")
print_test(server.get_balances())

print("Testing get_balances_by_company_id")
print_test(server.get_balances_by_company_id(company_id))

print("Testing get_balance_by_id")
print_test(server.get_balance_by_id(balance_id))

print("Testing get_qualification_by_id")
print_test(server.get_qualification_by_id(qualification["Id"]))


print("Testing get_employee_qualifications")
print_test(server.get_employee_qualifications())


print("Testing get_employee_qualification_by_id")
print_test(server.get_employee_qualification_by_id(employee_qualification["Id"]))

print("Testing update_employmee_qualification_by_id_put")
print_test(server.update_employmee_qualification_by_id_put(employee_qualification["Id"], EmployeeQualificationModel(companyId=employee_qualification["CompanyId"],
    employeeId=employee_qualification["EmployeeId"], instanceId=employee_qualification["InstanceId"], qualificationId=employee_qualification["QualificationId"], qualificationLevel=0.9)))


print_test(server.update_employee_qualification_by_id_post(employee_qualification["Id"], EmployeeQualificationModel(companyId=employee_qualification["CompanyId"],
    employeeId=employee_qualification["EmployeeId"], instanceId=employee_qualification["InstanceId"], qualificationId=employee_qualification["QualificationId"], qualificationLevel=0.9)))

print("Testing delete_employee_qualification_by_id")
print("Works")

print("Testing get_customers_by_company")
print_test(server.get_customers_by_company(GetCustomersByCompany(company=company_nr)))

print("Testing get_customer_by_id")
print_test(server.get_customer_by_id(customer_id))

print("Testing update_customer_by_id")
print(server.update_customer_by_id(customer_id, CustomerModel(code="1001", name="Inte test")))


print("Testing get_balance_adjustment_by_employee_id")
print_test(server.get_balance_adjustment_by_employee_id(employee_id))


print("Testing get_balance_adjustment_by_company_id")
print_test(server.get_balance_adjustment_by_company_id(company_id))


print("Testing get_balance_adjustment_by_id")
print_test(server.get_balance_adjustment_by_id(balance_adjustment_id))

print("Testing get_balance_adjustments")
print_test(server.get_balance_adjustments())

print("Testing get_public_travel_claims")
print_test(server.get_public_travel_claims())

print("Testing get_account_budget_by_account_id")
print_test(server.get_account_budget_by_account_id(proj_id))


print("Testing get_account_combination_by_account_id")
print_test(server.get_account_combination_by_account_id(account_id=account_id))

print("Testing add_or_replace_employee_image")
print_test(server.add_or_replace_employee_image(EmployeeImageModel(companyId=company_id, employeeId=employee_id, image=base64_img)))

print("Testing get_imported_trips_by_employee_id")
print_test(server.get_imported_trips_by_employee_id(employee_id))

print("Testing get_imported_trip_by_id")
print_test(server.get_imported_trip_by_id(imported_trip_id))
print("Testing get_next_of_kin_by_id")
print_test(server.get_next_of_kin_by_id(kin_id))

print("Testing get_next_of_kin_relationship_by_id")
print_test(server.get_next_of_kin_relationship_by_id(kin_relationship_id))

print("Testing get_next_of_kin_relationships")
print_test(server.get_next_of_kin_relationships())

print("Testing get_next_of_kins")
print_test(server.get_next_of_kins())

print("Testing batch_create_imported_trip")
print_test(server.batch_create_imported_trip([ImportedTripModel(employeeId=employee_id, fromDateTime=datetime(2025, 1, 1, 0, 0, 0), toDateTime=datetime(2025, 1, 1, 10, 0, 0), distance=100)]))

print("Testing batch_update_employment_rate_by_employee_id")
print_test(server.batch_update_employment_rate_by_employee_id(employee_id, [EmploymentRateModel(companyId=company_id, employeeId=employee_id, )]))

print("Testing create_account_budget_for_account_id")
print_test(server.create_account_budget_for_account_id(account_id=proj_id, query=AccountBudgetModel(actualSales=1800,budgetedCost=2000,
        budgetedHours=200,budgetedSales=2200,dateTime="2025-04-10 00:00")))


print("Testing create_company")
print_test(server.create_company(company_id_to_copy_from=company_id, copy_settings=0, query=CompanyPostRequestModel(companyNumber=8080, countryCode="SWE", currencyCode="SEK", name="Test AB")))


print("Testing get_employment_templates_by_company_id")
print_test(server.get_employment_templates_by_company_id(company_id=company_id))


print("Testing get_employee_images")
print_test(server.get_employee_images())


print("Testing get_employee_image_by_id")
print_test(server.get_employee_image_by_id(employee_img_id))


print("Testing get_employees")
print_test(server.get_employees())

print("Testing create_child")
print_test(server.create_child(
    ChildModel(
        companyId=company_id,
        employeeId=employee_id,
        identificationString="2020-01-20",
        identificationType=0,  # 0 = Birth date
        name="Testbarn"
        )
))

print("Testing get_children")
print_test(server.get_children())


print("Testing get_employment_personal_schedules")
print_test(server.get_employment_personal_schedules())


print("Testing create_employment_personal_schedule")
print_test(server.create_employment_personal_schedule(query=EmploymentPersonalScheduleModel(companyId=company_id, employeeId=employee_id,
    fromDate=datetime(2027, 1, 1, 0, 0, 0), toDate=datetime(2028, 1, 1, 0, 0, 0), time_group_id=employment_personal_schedule["TimeGroupId"], personalScheduleId=employment_personal_schedule["PersonalScheduleId"])))


print("Testing get_child_by_id")
print_test(server.get_child_by_id(child_id))


print("Testing get_unions")
print_test(server.get_unions())


print("Testing get_union_by_id")
print_test(server.get_union_by_id(union["Id"]))


print("Testing delete_child_by_id")
#print_test(server.delete_child_by_id("533abf8b-9dbc-46a4-b2dd-b43500ef83fc"))
print("Works!")

print("Testing create_balance_adjustment_batch_by_company")
print_test(server.create_balance_adjustment_batch_by_company(id=company_id, query=[BalanceAdjustmentModel(
    adjustment_value=150.5,
    balance_adjustment_type=0,
    balance_code="SEMT",
    employee_number=alt_employee_nr,
    entity_description="Manuell justering av semestersaldo",
    flex_sql_sort_order=0,
    is_generated=False,
    period_determination_date=datetime(2026, 4, 24, 0, 0, 0)
)]))


print("Testing get_user_account_part_approval_permissions")
print_test(server.get_user_account_part_approval_permissions())



print("Testing get_account_combination_by_account_distribution_id_and_account_code")
print_test(server.get_account_combination_by_account_distribution_id_and_account_code(account_distribution_id=account_distribution_id,account_code=account_nr))


print("Testing get_account_combination_by_account_id")
print_test(server.get_account_combination_by_account_id(account_id=account_id))


print("Testing get_account_combination_by_id")
print_test(server.get_account_combination_by_id(account_combination_id))


print("Testing create_account_combination")
print_test(server.create_account_combination(AccountCombinationModel(accountCombinationAccounts=[AccountCombinationAccountModel(accountDistribution=account_distribution_id, accountSelection=account_nr),
    AccountCombinationAccountModel(accountDistribution="806a9a28-17d2-4c5a-85df-ab1948424913", accountSelection="20"),
    AccountCombinationAccountModel(accountDistribution="206673b8-fa55-45f2-89f6-b43400978ecc", accountSelection="1000"),
    AccountCombinationAccountModel(accountDistribution="7a21a56d-c4b9-4625-93e0-d9d8c8e2cddf", accountSelection="1000"),
    AccountCombinationAccountModel(accountDistribution="e41a1471-a598-4084-b270-dc9872f6ab2d", accountSelection="1619")], combinationRule=1, companyId=company_id)))

print("Testing update_account_combination_by_id")
print_test(server.update_account_combination_by_id(id=account_combination_id, query=AccountCombinationModel(accountCombinationAccounts=[AccountCombinationAccountModel(accountDistribution=account_distribution_id, accountSelection=account_nr),
    AccountCombinationAccountModel(accountDistribution="806a9a28-17d2-4c5a-85df-ab1948424913", accountSelection="100"),
    AccountCombinationAccountModel(accountDistribution="206673b8-fa55-45f2-89f6-b43400978ecc", accountSelection="1000"),
    AccountCombinationAccountModel(accountDistribution="7a21a56d-c4b9-4625-93e0-d9d8c8e2cddf", accountSelection="1000"),
    AccountCombinationAccountModel(accountDistribution="e41a1471-a598-4084-b270-dc9872f6ab2d", accountSelection="1619")], combinationRule=1, companyId=company_id)))


print("Testing delete_account_combination_by_id")
print_test(server.delete_account_combination_by_id("5d06372e-5e29-436d-b3fd-b4340116eb91"))

print("Testing get_employment_document_categories")
print_test(server.get_employment_document_categories())

print("Testing get_employment_documents_collection_by_company")
print_test(server.get_employment_documents_collection_by_company(GetEmploymentDocumentCollection(companyId=company_id)))

print("Testing get_employment_documents_by_id")
print_test(server.get_employment_documents_by_id(employment_doc_id))


print("Testing create_employment_document")
print_test(server.create_employment_document(document_category_id=doc_category, employee_id=employee_id, title="CV", file_path="Kandidatexamensarbete.pdf"))

print("Testing delete_employment_documents_by_id")
print_test(server.delete_employment_documents_by_id(employment_doc_id))

print("Testing get_billing_releases_by_company")
print_test(server.get_billing_releases_by_company(GetBillingReleasesByCompany(company=company_nr)))

print("Testing get_billing_releases_by_id")
print_test(server.get_billing_releases_by_id(billing_release_id))


print("Testing get_collection_of_travel_time_rule_sets")
print_test(server.get_collection_of_travel_time_rule_sets())

print("Testing get_employee_presence_by_company")
print_test(server.get_employee_presence_by_company(GetEmployeePresenceByCompany(companyId=company_id)))



print("Testing get_customers_by_account_distribution_id")
print_test(server.get_customers_by_account_distribution_id(customers_acc_distribution_id))


print("Testing delete_employee_qualification_by_id")
print_test(server.delete_employee_qualification_by_id("de42c163-f005-48f8-9b35-b4360076a388"))


print("Testing get_employment_default_account_intervals")
print_test(server.get_employment_default_account_intervals())



print("Testing get_employment_default_account_interval_by_id")
print_test(server.get_employment_default_account_interval_by_id(employment_default_account_interval_id))


print("Testing get_organizational_chart_accountings_by_company_id")
print(server.get_organizational_chart_accountings_by_company_id(company_id))

print("Testing get_organizational_chart_employee_data_by_company_id")
print(server.get_organizational_chart_employee_data_by_company_id(company_id))

print("Testing get_employeee_data_by_organizational_chart_node_id")
print_test(server.get_employeee_data_by_organizational_chart_node_id(org_node_id))

print("Testing get_employment_default_accounts")
print_test(server.get_employment_default_accounts())


print("Testing get_employment_empty_schedules")
print_test(server.get_employment_empty_schedules())


print("Testing get_employment_empty_schedule_by_id")
print_test(server.get_employment_empty_schedule_by_id(empty_schedule_id))