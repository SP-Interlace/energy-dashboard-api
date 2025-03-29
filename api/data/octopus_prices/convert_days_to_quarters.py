import json

# Load the input JSON file
output_data = {}
for region in [chr(i) for i in range(ord("A"), ord("P") + 1)]:
    if region == "I" or region == "O":
        continue
    with open(f"energy_prices_gsp_{region}.json", "r") as f:
        monthly_data = json.load(f)

    # Create averages dictionary for region A
    averages_a = {month: data["average"] for month, data in monthly_data.items()}

    # Create output structure with all regions using the same averages
    output_data[region] = averages_a.copy()

# Write to output JSON file
with open("energy_prices_gsp_quarters.json", "w") as f:
    json.dump(output_data, f, indent=2)
