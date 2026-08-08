import uuid
import logging
from models import TripBundle, ComponentOption

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")

class SubAgentExecutor:
    def __init__(self, max_budget_ceiling: float):
        self.max_budget_ceiling = max_budget_ceiling

    def execute_booking(self, bundle: TripBundle) -> dict:
        if bundle.total_cost > self.max_budget_ceiling:
            raise ValueError(
                f"Budget Protection Triggered: Cost (${bundle.total_cost:.2f}) "
                f"exceeds ceiling (${self.max_budget_ceiling:.2f})."
            )

        flight_pnr = self._book_flight(bundle.flight)
        hotel_pnr = self._book_hotel(bundle.hotel)

        return {
            "status": "CONFIRMED",
            "flight_pnr": flight_pnr,
            "hotel_pnr": hotel_pnr,
            "guaranteed_cost": f"${bundle.total_cost:.2f}"
        }

    def _book_flight(self, flight: ComponentOption) -> str:
        logging.info(f"[FlightAgent] Booking {flight.provider} ({flight.details.get('route')}) @ ${flight.cost}")
        return f"FL-{uuid.uuid4().hex[:6].upper()}"

    def _book_hotel(self, hotel: ComponentOption) -> str:
        logging.info(f"[HotelAgent] Booking {hotel.provider} ({hotel.details.get('room_type')}) @ ${hotel.cost}")
        return f"HT-{uuid.uuid4().hex[:6].upper()}"