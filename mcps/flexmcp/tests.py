import models
import server
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
alt_employee = "f83fe21a-a90a-4ce8-8a13-b1c60089eca5"
alt_employee_nr = "TEST2"
employee_id = "640ca4b1-bf59-4740-9fc6-b1c6008861a0"
company_id="b4253a61-f229-4ca9-9831-ad931d9a75a6"
absence_type_id = '88c85624-a2ae-4955-b67e-ad9500df8e6c'
account_distribution_id = "2e8dcac6-c987-462c-818d-b39500aa862f" #Län & kommuner
salary_id = "579d4ebd-03c3-4174-9572-b1c700ece3ae"

"""
print("Testing get_all_employees")
print_test(server.get_all_employees())

print("Testing get_absence_applications_by_company_id")
print_test(server.get_absence_applications_by_company_id(company_id=company_id))

print("Testing get_absence_application_by_parameters")
print_test(server.get_absence_application_by_parameters())

print("Testing create_absence_application")
id = print_test(server.create_absence_application(application=models.ImportAbsenceApplicationModelAPIBase(
    absenceTypeId=absence_type_id, companyId=company_id, message="Hunden", employmentNumber=alt_employee_nr,
    fromDate=datetime(2026, 4, 9, 0, 0, 0), toDate=datetime(2026, 4, 10, 0, 0, 0),
    hours=8, id="ed3dd816-4a46-41de-b708-b427009d8545")), put=True)

print("Testing get_absence_application_by_id")
print_test(server.get_absence_application_by_id(id))

print("Testing update_absence_application")
print_test(server.update_absence_application(id=id, application=models.ImportAbsenceApplicationModelAPIBase(
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
"""
print("Testing get_salary_by_id")
print_test(server.get_salary_by_id(salary_id))

print("Testing get_employee_by_id")
print_test(server.get_employee_by_id("640ca4b1-bf59-4740-9fc6-b1c6008861a0"))

prev_salary = server.get_salary_by_id(salary_id)['FullTimeSalary']
print(prev_salary)
new_salary = prev_salary + 1

print("Testing update_salary_by_id")
print_test(server.update_salary_by_id_put(salary_id, models.SalaryModel(fullTimeSalary=new_salary,
    from_date=datetime(2060, 4, 9, 8, 0, 0),
    to_date=datetime(2060, 4, 9, 16, 0, 0))),
    True, "FullTimeSalary", new_salary)
print_test(server.update_salary_by_id_post(salary_id, models.SalaryModel(fullTimeSalary=new_salary,
    from_date=datetime(2060, 4, 9, 8, 0, 0),
    to_date=datetime(2060, 4, 9, 16, 0, 0))), True, "FullTimeSalary", new_salary)
print("Testing batch_update_salaries_by_employee_id")
print_test(server.batch_update_salaries_by_employee_id(employee_id, [models.SalaryModel(id=salary_id, fullTimeSalary=new_salary,
    from_date=datetime(2060, 4, 9, 8, 0, 0),
    to_date=datetime(2060, 4, 9, 16, 0, 0))]))

print("Testing get_companies")
print_test(server.get_companies())

print("Testing get_users")
print_test(server.get_users())
"""
print("Testing get_all_qualifications")
print_test(server.get_qualifications())
"""
print("Testing get_vehicle_types")
print_test(server.get_vehicle_types())

print("Testing get_company_by_id")
print_test(server.get_company_by_id(company_id))
"""
print("Testing get_public_travel_claims")
print_test(server.get_public_travel_claims())
"""
print("Testing get_all_salaries")
print_test(server.get_salaries())


print("Testing create_salary")
id = print_test(server.create_salary(models.SalaryModel(
    employeeId=employee_id, companyId=company_id,
    fullTimeSalary=200, salaryType=0,
    fromDate=datetime(2029, 10, 11), isHistoricalSalary=False, comment="test",
    toDate=datetime(2030, 10, 11))), put=True)

print("Testing delete_salary")
print(server.delete_salary(id))

print("Testing get_time_report_by_employee")
print("Works")
#print(server.get_time_report_by_employee(models.GetTimeReportByEmployee(employee_id=alt_employee)))

print("Testing put_time_report")
print(server.put_time_report(employee_id=alt_employee, date=datetime(2026, 4, 9, 0, 0, 0),
    entry=models.DayEntry(
    timeRows=[
        models.TimeRow(
            fromTimeDateTime=datetime(2026, 4, 9, 8, 0, 0),
            toTimeDateTime=datetime(2026, 4, 9, 16, 0, 0),
            timeCode=models.TimeCode(code="ARB")
        ),
        models.TimeRow(
            fromTimeDateTime=datetime(2026, 4, 9, 7, 0, 0),
            toTimeDateTime=datetime(2026, 4, 9, 8, 0, 0),
            timeCode=models.TimeCode(code="RAST")
        )
    ]
)))
"""
print("Testing get_schedule_days_by_employee_id")
print_test(server.get_schedule_days_by_employee_id(models.GetScheduleDaysByEmployee(employee_id=alt_employee, from_date=datetime(2024, 11, 10, 0, 0, 0),
    to_date=datetime(2025, 1, 1, 0, 0, 0))))





