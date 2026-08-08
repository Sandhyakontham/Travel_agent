import uuid
from typing import List, Tuple, Optional, Dict
from models import TravelConstraints, ComponentOption, TripBundle, GuaranteeLevel

class FeasibilityEngine:
    @staticmethod
    def evaluate(constraints: TravelConstraints, baseline_cost: float) -> Tuple[bool, float]:
        deficit = baseline_cost - constraints.max_budget
        return deficit <= 0, round(deficit, 2)

    @staticmethod
    def propose_alternatives(constraints: TravelConstraints) -> List[Dict]:
        return [
            {"action": "Reduce Duration", "proposed_days": max(1, constraints.duration_days - 1), "estimated_savings": 140.0},
            {"action": "Alternative Nearby Airport", "proposed_airport": "MDW (Midway)", "estimated_savings": 75.0},
            {"action": "Shift Dates", "proposed_shift": "+2 Days", "estimated_savings": 95.0}
        ]


class CombinatorialOptimizer:
    def __init__(self, flights: List[ComponentOption], hotels: List[ComponentOption]):
        self.flights = flights
        self.hotels = hotels

    def find_optimal_bundle(self, constraints: TravelConstraints) -> Optional[TripBundle]:
        best_bundle: Optional[TripBundle] = None
        max_utility = -1.0

        contingency = 50.0 if constraints.guarantee_level == GuaranteeLevel.LEVEL_3_FULL_TRIP else 30.0
        # Scaled realistic budget allowances
        food_allowance = 15.0 * constraints.duration_days * (constraints.adults + constraints.children * 0.5)
        transit_allowance = 10.0 * constraints.duration_days
        activity_allowance = 40.0

        fixed_allowance_total = contingency + food_allowance + transit_allowance + activity_allowance

        for flight in self.flights:
            for hotel in self.hotels:
                bundle_cost = flight.cost + hotel.cost + fixed_allowance_total

                if bundle_cost <= constraints.max_budget:
                    budget_margin = constraints.max_budget - bundle_cost
                    utility_score = (flight.score * 0.4) + (hotel.score * 0.4) + ((budget_margin / constraints.max_budget) * 0.2)

                    if utility_score > max_utility:
                        max_utility = utility_score
                        best_bundle = TripBundle(
                            bundle_id=str(uuid.uuid4())[:8],
                            flight=flight,
                            hotel=hotel,
                            transit_allowance=transit_allowance,
                            activity_allowance=activity_allowance,
                            food_allowance=food_allowance,
                            contingency_reserve=contingency
                        )

        return best_bundle