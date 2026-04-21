import models
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




print("Testing get_public_travel_claims")
print_test(server.get_public_travel_claims())

print("Testing get_account_combination_by_account_id")
print_test(server.get_account_combination_by_account_id(account_id=account_id))

print("Testing get_account_budget_by_account_id")
print_test(server.get_account_budget_by_account_id(account_id))



print("Testing get_balance_adjustment_by_employee_id")
print_test(server.get_balance_adjustment_by_employee_id(employee_id))


print("Testing get_balance_adjustment_by_company_id")
print_test(server.get_balance_adjustment_by_company_id(company_id))


print("Testing get_balance_adjustments")
print_test(server.get_balance_adjustments())
