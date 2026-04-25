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
                print(str(input)[:500])
        elif "Id" in input:
            print("Works")
        else:
            print("Does not work!")
            print(str(input)[:500])

#print("Testing list_instances")
#print_test(server.list_instances())
"""
print("Testing get_background_tasks")
print_test(server.get_background_tasks())



print("Testing get_background_tasks_by_id")
print_test(server.get_background_tasks_by_id())
print("Testing create_new_accounts")
print(server.create_new_accounts(
    account_distribution_id=account_distribution_id,
    account_model=AccountModel(
        code="0999", name="Atlantis", billing=AccountBillingModel(priceRows=[
            AccountBillingPriceRowModel(id="e41a1471-a598-4084-b270-dc9872f6ab2d", )
        ])
    )
))



print("Testing get_public_travel_claims")
print_test(server.get_public_travel_claims())



print("Testing get_account_budget_by_account_id")
print_test(server.get_account_budget_by_account_id(account_id))

print("Testing get_background_tasks")
print(server.get_background_tasks())


print("Testing get_balances_by_company_id")
print_test(server.get_balances_by_company_id(company_id))

print("Testing get_balance_by_id")
print_test(server.get_balance_by_id(balance_id))



print("Testing create_company_account_part_approval_permissions_by_user_id")
print(server.create_company_account_part_approval_permissions_by_user_id(user_id, AccountDistributionPartApprovalPermissionModel(account_distribution_id=account_distribution_id,
    id=account_approval_permission_id,
    premission_to_account_without_row_or_account=True, premission_to_all_accounts=True, user_id=user_id)))


print("Testing create_balance_adjustment_batch_by_company")
print(server.create_balance_adjustment_batch_by_company(balance["CompanyId"], 
    [BalanceAdjustmentModel(balance_adjustment_type=2, balance_code=balance["Code"],
    employee_number=alt_employee_nr, is_generated=True, period_determination_date=datetime(2025, 1, 1, 0, 0, 0))]))





print("Testing begin_background_task_rollback_release")
print_test(server.begin_background_task_rollback_release(RollbackReleaseModel()))




print("Testing begin_background_task_release_accounts_to_billing")
print_test(server.begin_background_task_release_accounts_to_billing(BillingReleaseSelectionModel(company=company_id)))



print("Testing check_status")
print_test(server.check_status())



for account in account_distributions:
    print(account["Description"])
    print(account["Id"])
    print(server.get_accounts_by_account_distribution_id(account_distribution_id=account["Id"]))




print("Testing get_balance_report_by_balance_id_and_employee_id")
print_test(server.get_balance_report_by_balance_id_and_employee_id(balance_id))

print("Testing get_company_information")
print_test(server.get_company_information(start_range=1000, end_range=2000))

print("Testing get_employment_type_by_id")
print_test(server.get_employment_type_by_id(employment_type_id))


print("Testing get_employment_vacation_by_id")
print_test(server.get_employment_vacation_by_id(employment_vacation_id))


print("Testing get_hr_form_document_template_by_id")
print_test(server.get_hr_form_document_template_by_id(employment_doc_id))


print("Testing get_payroll_run_employments")
print(server.get_payroll_run_employments())

print("Testing get_payroll_run_by_id")
print_test(server.get_payroll_run_by_id())

print("Testing get_payroll_run_employee_by_id")
print_test(server.get_payroll_run_employee_by_id())

print("Testing get_payroll_run_transaction_account_collectioion_by_id")
print_test(server.get_payroll_run_transaction_account_collectioion_by_id())

print("Testing get_payroll_run_transaction_account_collections")
print_test(server.get_payroll_run_transaction_account_collections())

print("Testing get_payroll_run_transaction_by_id")
print_test(server.get_payroll_run_transaction_by_id())


print("Testing get_time")
print_test(server.get_time())



"""



"""
print(server.create_new_accounts(
    account_distribution_id=test_dist_id,
    account_model=AccountModel(
        billingStateEnum=2, travelBillingStateEnum=2,
        code="0999", name="Atlantis", billing=AccountBillingModel(priceRows=[AccountBillingPriceRowModel(
            accounts=[AccountBillingPriceRowAccountModel(
                account_id=account_id, id="11111111-1111-1111-1111-111111111111"
            )],
            price=100,
            unit=0
        )]))
))

for account in account_distributions:
    print(account["Description"])
    print(account["Id"])
    print(server.get_accounts_by_account_distribution_id(account_distribution_id=account["Id"]))
    
print("Testing create_employee")
print(server.create_employee(EmployeeCreateParams(employmenttemplateId="a725a788-6d67-4a75-b3e9-b0e700fa3882"), EmployeeCreateModel(
    companyId=company_id,
    #nationality="SE - Sverige",
    #date_of_birth=datetime(1960, 7, 5),
    employment=[EmploymentModel(employmentNumber="1")],
    firstName="Test",
    lastName="Testsson",
    name="Test Testsson",
    #national_identification_number="19600705-6341"
)))
    """

print("Testing get_employee_by_id")
print(server.get_employee_by_id(employee_id))
print("Testing get_stamping_by_userID")
print(server.get_stamping_by_userID(query=GetStampingByUserId(user_id=test_user_id)))
print("Testing update_stamping_by_employee_id")
print_test(server.update_stamping_by_employee_id(query=UpdateStampingByEmployeeId(employee_id=test_employee_id, date_time=datetime(2026, 4, 25, 12)), body=[StampingAccountModel(
    accountCode=account_nr, accountDistributionId=konto_acc_dist_id)]))

print("Testing update_stamping_by_user_id")
print_test(server.update_stamping_by_user_id(query=UpdateStampingByUserId(user_id=test_user_id), body=StampingAccountModel(
    accountCode=account_nr, accountDistributionId=konto_acc_dist_id)))


"""


print("Testing update_role_collection_of_user_for_employee_post")
print_test(server.update_role_collection_of_user_for_employee_post())


print("Testing update_role_collection_of_user_for_employee_put")
print_test(server.update_role_collection_of_user_for_employee_put())
print("Testing update_role_collection_of_user_for_company_post")
print_test(server.update_role_collection_of_user_for_company_post(query=UpdateRoleCollectionOfUserForCompany(userId=test_user_id, companyId=company_id), 
    body=[RoleModel(id=role_id, name="Testroll") ]))

print("Testing get_organizational_chart_node_by_id")
print_test(server.get_organizational_chart_node_by_id())




print("Testing update_role_collection_of_user_for_comapany_put")
print_test(server.update_role_collection_of_user_for_comapany_put())




print("Testing update_role_collection_on_account_for_user_post")
print_test(server.update_role_collection_on_account_for_user_post())

print("Testing update_role_collection_on_account_for_user_put")
print_test(server.update_role_collection_on_account_for_user_put())











print("Testing get_public_travel_claim_attachment_by_id")
print_test(server.get_public_travel_claim_attachment_by_id())

print("Testing get_reminders_by_user_id")
print_test(server.get_reminders_by_user_id())


print("Testing get_salary_basis_by_salary_transfer_id")
print_test(server.get_salary_basis_by_salary_transfer_id())

print("Testing get_salary_basis_by_travel_salary_transfer_id")
print_test(server.get_salary_basis_by_travel_salary_transfer_id())

print("Testing get_salary_statistic_by_employment_period_id")
print_test(server.get_salary_statistic_by_employment_period_id())

print("Testing get_salary_transfer_by_id")
print_test(server.get_salary_transfer_by_id())

print("Testing get_schedule_days_by_salary_transfer_id")
print_test(server.get_schedule_days_by_salary_transfer_id())

print("Testing get_settled_payslip_by_payroll_run_employee_id")
print_test(server.get_settled_payslip_by_payroll_run_employee_id())




print("Testing get_time_registration_settings_by_company_id")
print_test(server.get_time_registration_settings_by_company_id())

print("Testing get_time_report_audit_levels_by_comppany_id")
print_test(server.get_time_report_audit_levels_by_comppany_id())

print("Testing get_time_report_by_employee_id")
print_test(server.get_time_report_by_employee_id())

print("Testing get_time_reports_by_employee_id")
print_test(server.get_time_reports_by_employee_id())

print("Testing get_to_time_schedule_by_employee_and_date")
print_test(server.get_to_time_schedule_by_employee_and_date())

print("Testing get_travel_claim_audit_levels_by_company_id")
print_test(server.get_travel_claim_audit_levels_by_company_id())



print("Testing get_user_account_part_approval_permission_by_id")
print_test(server.get_user_account_part_approval_permission_by_id())













print("Testing create_company_account_part_approval_permissions_by_user_id")
print_test(server.create_company_account_part_approval_permissions_by_user_id(user_id, AccountDistributionPartApprovalPermissionModel(
    accountDistributionId=account_distribution_id, id=user_acc_approval["AccountDistributionPartApprovalPermissionId"],
    premissionToAccountWithoutRowOrAccount=False, premissionToAllAccounts=False, userId=user_id)))

print("Testing create_employment_default_account_interval")
print_test(server.create_employment_default_account_interval())

print("Testing create_employment_default_accunt")
print_test(server.create_employment_default_accunt())



print("Testing create_employment_public_schedule")
print_test(server.create_employment_public_schedule())

print("Testing create_employment_rate")
print_test(server.create_employment_rate())

print("Testing create_employment_title")
print_test(server.create_employment_title())

print("Testing create_employment_vehicle")
print_test(server.create_employment_vehicle())

print("Testing create_hr_form")
print_test(server.create_hr_form())

print("Testing create_imported_trip")
print_test(server.create_imported_trip())

print("Testing create_new_accounts")
print_test(server.create_new_accounts())



print("Testing create_user_account_part_approval_permission_by_account_distribution_part_approval_permission_id")
print_test(server.create_user_account_part_approval_permission_by_account_distribution_part_approval_permission_id())




print("Testing delete_balance_adjustment_by_id")
print_test(server.delete_balance_adjustment_by_id())


print("Testing delete_compamny_account_approval_permission_by_id")
print_test(server.delete_compamny_account_approval_permission_by_id())

print("Testing delete_customer_by_id")
print_test(server.delete_customer_by_id())

print("Testing delete_employee_image_by_id")
print_test(server.delete_employee_image_by_id())


print("Testing delete_employment_default_account_interval_by_id")
print_test(server.delete_employment_default_account_interval_by_id())

print("Testing delete_employment_default_accunt_by_id_")
print_test(server.delete_employment_default_accunt_by_id_())



print("Testing delete_employment_personal_schedule_by_id")
print_test(server.delete_employment_personal_schedule_by_id())

print("Testing delete_employment_public_schedule_by_id")
print_test(server.delete_employment_public_schedule_by_id())

print("Testing delete_employment_rate_by_id")
print_test(server.delete_employment_rate_by_id())

print("Testing delete_employment_title_by_id")
print_test(server.delete_employment_title_by_id())

print("Testing delete_employment_vehicle_by_id")
print_test(server.delete_employment_vehicle_by_id())

print("Testing delete_hr_form__by_id")
print_test(server.delete_hr_form__by_id())




print("Testing delete_user_account_part_approval_permission_by_id")
print_test(server.delete_user_account_part_approval_permission_by_id())





print("Testing import_company")
print_test(server.import_company())


print("Testing insert_time_row")
print_test(server.insert_time_row())

print("Testing load_dotenv")
print_test(server.load_dotenv())

print("Testing model_validator")
print_test(server.model_validator())

print("Testing post_customers_by_account_distribution_id")
print_test(server.post_customers_by_account_distribution_id())

print("Testing to_api_time_row")
print_test(server.to_api_time_row())

print("Testing update_account_budget_by_id")
print_test(server.update_account_budget_by_id())

print("Testing update_account_by_id")
print_test(server.update_account_by_id())


print("Testing update_balance_adjustment_by_id")
print_test(server.update_balance_adjustment_by_id())

print("Testing update_child_by_id_post")
print_test(server.update_child_by_id_post())

print("Testing update_child_by_id_put")
print_test(server.update_child_by_id_put())

print("Testing update_company_account_part_aproval_permission_by_id")
print_test(server.update_company_account_part_aproval_permission_by_id())



print("Testing update_employment_default_account_interval_by_id_post")
print_test(server.update_employment_default_account_interval_by_id_post())

print("Testing update_employment_default_account_interval_by_id_put")
print_test(server.update_employment_default_account_interval_by_id_put())

print("Testing update_employment_default_accunt_by_id_post")
print_test(server.update_employment_default_accunt_by_id_post())

print("Testing update_employment_default_accunt_by_id_put")
print_test(server.update_employment_default_accunt_by_id_put())




print("Testing update_employment_personal_schedule_by_id_post")
print_test(server.update_employment_personal_schedule_by_id_post())

print("Testing update_employment_personal_schedule_by_id_put")
print_test(server.update_employment_personal_schedule_by_id_put())

print("Testing update_employment_public_schedule_by_id_post")
print_test(server.update_employment_public_schedule_by_id_post())

print("Testing update_employment_public_schedule_by_id_put")
print_test(server.update_employment_public_schedule_by_id_put())

print("Testing update_employment_rate_by_id_post")
print_test(server.update_employment_rate_by_id_post())

print("Testing update_employment_rate_by_id_put")
print_test(server.update_employment_rate_by_id_put())

print("Testing update_employment_title_by_id_post")
print_test(server.update_employment_title_by_id_post())

print("Testing update_employment_title_by_id_put")
print_test(server.update_employment_title_by_id_put())

print("Testing update_employment_vaction_by_id_post")
print_test(server.update_employment_vaction_by_id_post())

print("Testing update_employment_vaction_by_id_put")
print_test(server.update_employment_vaction_by_id_put())

print("Testing update_employment_vehicle_by_id")
print_test(server.update_employment_vehicle_by_id())

print("Testing update_hr_form_by_id")
print_test(server.update_hr_form_by_id())


print("Testing update_overtime_marking_on_time_report_day_by_employee_id")
print_test(server.update_overtime_marking_on_time_report_day_by_employee_id())

print("Testing update_own_assessment_field_value_by_id_post")
print_test(server.update_own_assessment_field_value_by_id_post())

print("Testing update_own_assessment_field_value_by_id_put")
print_test(server.update_own_assessment_field_value_by_id_put())

print("Testing update_pension_and_insurance_setting_by_employee_id_post")
print_test(server.update_pension_and_insurance_setting_by_employee_id_post())

print("Testing update_pension_and_insurance_setting_by_employee_id_put")
print_test(server.update_pension_and_insurance_setting_by_employee_id_put())


print("Testing update_resignation_cause_by_id_post")
print_test(server.update_resignation_cause_by_id_post())

print("Testing update_resignation_cause_by_id_put")
print_test(server.update_resignation_cause_by_id_put())

print("Testing update_salary_statistic_by_employment_period_id_post")
print_test(server.update_salary_statistic_by_employment_period_id_post())

print("Testing update_salary_statistic_by_employment_period_id_put")
print_test(server.update_salary_statistic_by_employment_period_id_put())

print("Testing update_user_account_part_approval_permission_by_id")
print_test(server.update_user_account_part_approval_permission_by_id())



"""