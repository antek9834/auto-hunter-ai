
from tools.fuel_tools import calculate_fuel_cost, calculate_additional_consumption

class FuelCostAnalysisService:
    
    def analyze(self, km_per_month, avg_consumption, fuel_price, avg_person_weight=None, num_people=None):
        result = calculate_fuel_cost(
            km_per_month, avg_consumption, fuel_price
        )

        additional = 0
        if avg_person_weight and num_people:
            additional = calculate_additional_consumption(avg_person_weight, num_people)

        result["additional_consumption"] = additional
        result["final_consumption"] = avg_consumption + additional

        return result
