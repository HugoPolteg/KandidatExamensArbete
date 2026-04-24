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








print("Testing get_projects")
print(server.get_projects(company_nr))


print("Testing get_all_roles_of_account")
print_test(server.get_all_roles_of_account(GetAllRolesOfAccount(userId=user_id, companyId=company_id, accountId=account_id)))


print("Testing get_all_roles_of_user_for_company")
print_test(server.get_all_roles_of_user_for_company(GetAllRolesOfUserForCompany(userId=user_id, companyId=company_id)))


print("Testing get_all_roles_of_user_for_employee")
print_test(server.get_all_roles_of_user_for_employee(GetAllRolesOfUserForEmployee(userId=user_id, companyId=company_id, employeeId=employee_id)))

print("Testing get_invocing_basis_by_billing_release_id")
print_test(server.get_invoicing_basis_by_billing_release_id(billing_release_id))


