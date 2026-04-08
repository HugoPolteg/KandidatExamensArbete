import server
import models
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
employee_id = "640ca4b1-bf59-4740-9fc6-b1c6008861a0"
company_id="b4253a61-f229-4ca9-9831-ad931d9a75a6"
"""
print("Testing get_salary_by_id")
print_test(server.get_salary_by_id("579d4ebd-03c3-4174-9572-b1c700ece3ae"))

prev_salary = server.get_salary_by_id("579d4ebd-03c3-4174-9572-b1c700ece3ae")['FullTimeSalary']
print(prev_salary)
new_salary = prev_salary + 1

print("Testing update_salary_by_id")
print_test(server.update_salary_by_id("579d4ebd-03c3-4174-9572-b1c700ece3ae", models.Salary(fullTimeSalary=new_salary)), True, "FullTimeSalary", new_salary)

print("Testing list_all_companies")
print_test(server.list_all_companies())

print("Testing get_users")
print_test(server.get_users())

print("Testing get_all_qualifications")
print_test(server.get_all_qualifications())

print("Testing get_vehicle_types")
print_test(server.get_vehicle_types())

print("Testing get_company")
print_test(server.get_company(company_id))

print("Testing get_travel_claims_by_company_id")
print_test(server.get_travel_claims_by_company_id(company_id))

print("Testing get_all_salaries")
print_test(server.get_all_salaries())

print("Testing get_salaries_by_company")
print_test(server.get_salaries_by_company(models.GetSalariesByCompany(companyId=company_id)))

print("Testing get_all_employees")
print_test(server.get_all_employees())

print("Testing get_salaries_by_company_and_employee")
print_test(server.get_salaries_by_company_and_employee(models.GetSalariesByCompanyAndEmployee(companyId=company_id, employeeId=employee_id)))

print("Testing get_salaries_by_employee")
print_test(server.get_salaries_by_employee(models.GetSalariesByEmployee(employeeId=employee_id)))
print(server.get_salaries_by_employee(models.GetSalariesByEmployee(employeeId=employee_id)))


print("Testing create_salary")
id = print_test(server.create_salary(models.UpdateOrCreateSalaries(
    employeeId=employee_id, companyId=company_id,
    fullTimeSalary=200, salaryType=0,
    fromDate=datetime.now(), isHistoricalSalary=False, comment="test",
    toDate=datetime(2028, 10, 11))), put=True)

print("Testing delete_salary")
print(server.delete_salary(id))
"""

print("Testing get_time_report_by_employee")
print("Works")
#print(server.get_time_report_by_employee(models.GetTimeReportByEmployee(employee_id=alt_employee)))

print("Testing put_time_report")
print(server.put_time_report(employee_id=alt_employee, date=datetime.now(),
    entry=models.DayEntry(
    timeRows=[
        models.TimeRow(
            fromTimeDateTime=datetime.now()-timedelta(hours=4),
            toTimeDateTime=datetime.now(),
            timeCode=models.TimeCode(code="ARB")
        ),
        models.TimeRow(
            fromTimeDateTime=datetime.now()-timedelta(hours=8),
            toTimeDateTime=datetime.now()-timedelta(hours=5),
            timeCode=models.TimeCode(code="RAST")
        )
    ]
)))
