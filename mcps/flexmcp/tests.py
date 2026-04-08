import server

def print_test(input):
    print(str(input)[:120])

#print("Testing list_instances")
#print_test(server.list_instances())

print("Testing list_all_companies")
print_test(server.list_all_companies())

print("Testing get_users")
print_test(server.get_users())

print("Testing get_all_qualifications")
print_test(server.get_all_qualifications())

print("Testing get_qualifications_by_instance")
print_test(server.get_qualifications_by_instance())

print("Testing get_vehicle_type")
print_test(server.get_vehicle_type())

print("Testing get_company")
print_test(server.get_company("660f16e7-183e-4541-9570-028993ab21b6"))

print("Testing get_salaries_by_instance")
print_test(server.get_salaries_by_instance())

print("Testing get_travel_claims_by_company_id")
print_test(server.get_travel_claims_by_company_id("660f16e7-183e-4541-9570-028993ab21b6"))

print("Testing get_all_salaries")
print_test(server.get_salary_by_id())