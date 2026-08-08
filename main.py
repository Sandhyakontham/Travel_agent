from models import ComponentOption
from groq_service import GroqNLParser
from engines import FeasibilityEngine, CombinatorialOptimizer
from sub_agents import SubAgentExecutor

def main():
    user_prompt = (
        "Plan a 5-day trip to Chicago (ORD) from Raleigh (RDU) for 2 adults and 2 kids "
        "with a strict maximum budget of $1000."
    )

    print("=== 1. NATURAL LANGUAGE PARSING (GROQ LLM) ===")
    parser = GroqNLParser()
    constraints = parser.parse_user_prompt(user_prompt)
    
    print(f"Parsed Constraints:")
    print(f"  Origin: {constraints.origin} | Destination: {constraints.destination}")
    print(f"  Duration: {constraints.duration_days} Days | Travelers: {constraints.adults}A, {constraints.children}C")
    print(f"  Hard Budget Cap: ${constraints.max_budget:.2f}\n")

    # Mock dynamic search results with budget-friendly options
    available_flights = [
        ComponentOption("F1", "Flight", "Frontier Airlines", 220.0, 0.70, {"route": "RDU-ORD Non-stop"}),
        ComponentOption("F2", "Flight", "American Airlines", 350.0, 0.85, {"route": "RDU-ORD Non-stop"}),
    ]

    available_hotels = [
        ComponentOption("H1", "Hotel", "Holiday Inn Express", 240.0, 0.78, {"room_type": "Standard 2 Double"}),
        ComponentOption("H2", "Hotel", "Hyatt Regency Loop", 380.0, 0.88, {"room_type": "2 Queen Suite"}),
    ]

    print("=== 2. FEASIBILITY & OPTIMIZATION ===")
    min_baseline = min(f.cost for f in available_flights) + min(h.cost for h in available_hotels) + 150.0
    is_feasible, deficit = FeasibilityEngine.evaluate(constraints, min_baseline)

    if not is_feasible:
        print(f"Trip not feasible under budget cap. Shortfall: ${deficit:.2f}")
        return

    optimizer = CombinatorialOptimizer(available_flights, available_hotels)
    bundle = optimizer.find_optimal_bundle(constraints)

    if not bundle:
        print("No bundle fits the strict budget constraints.")
        return

    print(f"Selected Bundle ID: {bundle.bundle_id}")
    print(f"Total Bundle Cost: ${bundle.total_cost:.2f} (Under ${constraints.max_budget:.2f} cap)")

    summary_input = f"Flight: {bundle.flight.provider} (${bundle.flight.cost}), Hotel: {bundle.hotel.provider} (${bundle.hotel.cost}), Total: ${bundle.total_cost:.2f}"
    ai_summary = parser.summarize_itinerary_reasoning(summary_input)
    print(f"\nAI Justification:\n{ai_summary}\n")

    print("=== 3. ATOMIC BOOKING EXECUTION ===")
    executor = SubAgentExecutor(max_budget_ceiling=constraints.max_budget)
    result = executor.execute_booking(bundle)

    print("\n[BOOKING COMPLETE]")
    print(f"Status: {result['status']}")
    print(f"Flight PNR: {result['flight_pnr']}")
    print(f"Hotel PNR:  {result['hotel_pnr']}")
    print(f"Guaranteed Total: {result['guaranteed_cost']}")

if __name__ == "__main__":
    main()