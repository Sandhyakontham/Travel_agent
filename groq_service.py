import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL
from models import ParsedTravelRequest, TravelConstraints, GuaranteeLevel

class GroqNLParser:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)

    def parse_user_prompt(self, user_prompt: str) -> TravelConstraints:
        schema = ParsedTravelRequest.model_json_schema()

        system_instructions = (
            "You are a precision travel requirement extractor.\n"
            "Extract structured travel parameters from the user's input.\n"
            "You MUST return a single top-level JSON object with NO nested parent keys.\n\n"
            f"Target JSON Schema:\n{json.dumps(schema, indent=2)}\n\n"
            "Example valid response:\n"
            '{\n'
            '  "origin": "RDU",\n'
            '  "destination": "ORD",\n'
            '  "duration_days": 5,\n'
            '  "adults": 2,\n'
            '  "children": 2,\n'
            '  "max_budget": 1000.0,\n'
            '  "family_friendly": true\n'
            '}'
        )

        response = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )

        raw_json = response.choices[0].message.content
        data = json.loads(raw_json)

        if len(data) == 1 and isinstance(list(data.values())[0], dict):
            data = list(data.values())[0]

        parsed = ParsedTravelRequest.model_validate(data)

        return TravelConstraints(
            origin=parsed.origin,
            destination=parsed.destination,
            duration_days=parsed.duration_days,
            adults=parsed.adults,
            children=parsed.children,
            max_budget=parsed.max_budget,
            guarantee_level=GuaranteeLevel.LEVEL_2_TRIP_COST
        )

    def summarize_itinerary_reasoning(self, bundle_summary: str) -> str:
        prompt = f"Provide a brief 2-3 sentence executive justification for this optimized budget travel package:\n{bundle_summary}"
        
        response = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()