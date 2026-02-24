import json

car_brands_data = []
with open("car_brands.json", "r") as file:
    car_brands_data = json.load(file)

car_brands = car_brands_data["car_brands"]

find_code = "22222"
result = next((brand for brand in car_brands if brand["code"] == find_code), None)
if result:
    print(result["name"])
else:
    print("Unknown")