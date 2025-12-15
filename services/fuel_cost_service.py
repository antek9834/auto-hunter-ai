import pandas as pd
from tools.fuel_tools import calculate_fuel_cost, calculate_additional_consumption

# Import for Langfuse
try:
    from langfuse.decorators import observe
except ImportError:
    def observe(*args, **kwargs):
        def decorator(func): return func
        return decorator

class FuelCostAnalysisService:
    
    @observe(as_type="span")
    def analyze(self, km_per_month, avg_consumption, fuel_price, avg_person_weight=None, num_people=None):
        result = calculate_fuel_cost(
            km_per_month, avg_consumption, fuel_price
        )
        # using tools as LLM are unreliable for math to ensure 100% accuracy for financial calculations - form Week 5
        additional = 0
        if avg_person_weight and num_people:
            additional = calculate_additional_consumption(avg_person_weight, num_people)

        # creating table for better visibility
        final_consumption = avg_consumption + additional
        
        table_data = [
            {"Metric": "Base Consumption", "Value": f"{avg_consumption} L/100km"},
            {"Metric": "Additional Load Impact", "Value": f"{additional:.2f} L/100km"},
            {"Metric": "Final Consumption", "Value": f"{final_consumption:.2f} L/100km"},
            {"Metric": "Monthly Cost", "Value": f"{result.get('monthly_cost', 0):.2f} €"},
            {"Metric": "Yearly Cost", "Value": f"{result.get('yearly_cost', 0):.2f} €"}
        ]

        return pd.DataFrame(table_data)