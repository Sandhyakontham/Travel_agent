from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class GuaranteeLevel(str, Enum):
    LEVEL_1_BOOKING = "LEVEL_1_BOOKING"
    LEVEL_2_TRIP_COST = "LEVEL_2_TRIP_COST"
    LEVEL_3_FULL_TRIP = "LEVEL_3_FULL_TRIP"

class ParsedTravelRequest(BaseModel):
    origin: str = Field(description="Origin airport code or city name, e.g., RDU")
    destination: str = Field(description="Destination airport code or city name, e.g., ORD")
    duration_days: int = Field(description="Trip duration in days")
    adults: int = Field(default=1, description="Number of adult travelers")
    children: int = Field(default=0, description="Number of child travelers")
    max_budget: float = Field(description="Maximum total budget ceiling in USD")
    family_friendly: bool = Field(default=True, description="Whether family friendly options are preferred")

@dataclass
class TravelConstraints:
    origin: str
    destination: str
    duration_days: int
    adults: int
    children: int
    max_budget: float
    guarantee_level: GuaranteeLevel = GuaranteeLevel.LEVEL_2_TRIP_COST
    soft_preferences: Dict[str, float] = field(default_factory=lambda: {
        "family_friendly": 0.8,
        "location_centrality": 0.7,
        "transit_convenience": 0.9
    })

@dataclass
class ComponentOption:
    id: str
    category: str
    provider: str
    cost: float
    score: float
    details: Dict

@dataclass
class TripBundle:
    bundle_id: str
    flight: ComponentOption
    hotel: ComponentOption
    transit_allowance: float
    activity_allowance: float
    food_allowance: float
    contingency_reserve: float

    @property
    def total_cost(self) -> float:
        return (
            self.flight.cost +
            self.hotel.cost +
            self.transit_allowance +
            self.activity_allowance +
            self.food_allowance +
            self.contingency_reserve
        )

    @property
    def total_score(self) -> float:
        return round((self.flight.score + self.hotel.score) / 2.0, 2)