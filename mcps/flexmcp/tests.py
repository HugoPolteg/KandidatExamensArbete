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


"""
print("Testing create_new_accounts")
print(server.create_new_accounts(
    account_distribution_id=account_distribution_id,
    account_model=models.AccountModel(
        code="0999", name="Atlantis", billing=models.AccountBillingModel(priceRows=[
            models.AccountBillingPriceRowModel(id="e41a1471-a598-4084-b270-dc9872f6ab2d", )
        ])
    )
))



print("Testing get_public_travel_claims")
print_test(server.get_public_travel_claims())


print("Testing get_account_combination_by_account_id")
print_test(server.get_account_combination_by_account_id(account_id=account_id))

print("Testing get_account_budget_by_account_id")
print_test(server.get_account_budget_by_account_id(account_id))

print("Testing get_background_tasks")
print(server.get_background_tasks())


print("Testing get_balances_by_company_id")
print_test(server.get_balances_by_company_id(company_id))

print("Testing get_balance_by_id")
print_test(server.get_balance_by_id(balance_id))



print("Testing create_company_account_part_approval_permissions_by_user_id")
print(server.create_company_account_part_approval_permissions_by_user_id(user_id, models.AccountDistributionPartApprovalPermissionModel(account_distribution_id=account_distribution_id,
    id=account_approval_permission_id,
    premission_to_account_without_row_or_account=True, premission_to_all_accounts=True, user_id=user_id)))


print("Testing create_balance_adjustment_batch_by_company")
print(server.create_balance_adjustment_batch_by_company(balance["CompanyId"], 
    [models.BalanceAdjustmentModel(balance_adjustment_type=2, balance_code=balance["Code"],
    employee_number=alt_employee_nr, is_generated=True, period_determination_date=datetime(2025, 1, 1, 0, 0, 0))]))

"""

print("Testing create_new_accounts")
print(server.create_new_accounts(
    account_distribution_id=account_distribution_id,
    account_model=models.AccountModel(
        billingStateEnum=2, travelBillingStateEnum=2,
        code="0999", name="Atlantis", billing=models.AccountBillingModel(priceRows=[models.AccountBillingPriceRowModel(
            accounts=[models.AccountBillingPriceRowAccountModel(
                account_id=account_id, id="11111111-1111-1111-1111-111111111111"
            )],
            price=100,
            unit=0
        )]))
))

print(server.update_customer_by_id(customer_id, models.CustomerModel(code="1001", name="Inte test")))
