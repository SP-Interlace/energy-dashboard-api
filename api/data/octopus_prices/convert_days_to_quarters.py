import json

# Load the input JSON file
with open("energy_prices_gsp_A.json", "r") as f:
    monthly_data = json.load(f)

# Create averages dictionary for region A
averages_a = {month: data["average"] for month, data in monthly_data.items()}

# Generate all region labels A-P (16 regions)
regions = [chr(i) for i in range(ord("A"), ord("P") + 1)]

# Create output structure with all regions using the same averages
output_data = {region: averages_a.copy() for region in regions}

# Write to output JSON file
with open("energy_prices_gsp_quarters.json", "w") as f:
    json.dump(output_data, f, indent=2)
