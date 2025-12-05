
def calculate_additional_consumption(avg_person_weight: float, num_people: int):
    """
    Additional fuel consumption per 100 km.
    """
    return (avg_person_weight * num_people * 0.5) / 100


def calculate_fuel_cost(km_per_month: float, avg_consumption: float, fuel_price: float):
    liters_used = (km_per_month / 100) * avg_consumption
    monthly_cost = liters_used * fuel_price
    yearly_cost = monthly_cost * 12
    
    return {
        "liters_used": liters_used,
        "monthly_cost": monthly_cost,
        "yearly_cost": yearly_cost
    }
