from memory.db import DB
from agents.basicAgent import BasicAgent
from langchain_core.prompts import PromptTemplate
import re
import json

class JsonAgent(BasicAgent):
  def __init__(self, input_data=None, role=None, extra_info=None):
    super().__init__(input_data=input_data, role="JsonAgent")
    self.db = DB()

  def create_prompt_template(self):
     template = """
     You are a webhook data parser.
     Your job is to carefully parse the json webhook data and check whether it matches the schema given
     The schema is as follows (the values given are dummy but this is the format of the values, carefully analyze the possibility of values before answering):
     {{
        "event_type": "order_created",
        "timestamp": "2025-06-02T15:30:00Z",
        "source": "helloecommerce",
        "payload": {{
        "order_id": "ORD-102",
        "user_id": "USR-777",
        "items": [
          {{
            "item_id": "SKU-123",
            "name": "Wireless Mouse",
            "quantity": 2,
            "unit_price": 599.00
          }},
          {{
            "item_id": "SKU-456",
            "name": "Keyboard",
            "quantity": 1,
            "unit_price": 699.00
          }}
        ],
        "currency": "INR",
        "total": 1398,
        "payment_status": "paid",
        "shipping_address": {{
        "name": "XYZ",
        "address_line1": "123 Main St",
        "city": "Delhi",
        "postal_code": "12345",
        "country": "India"
      }}
    }}
  }}
  Your key role is to parse and summarize the key fields (i.e "event_type","timestamp","source","payload")
  You also need to make sure the webhook data matches the dummy schema. Along with that, make sure the values of the keys of the input webhook are type compatible to the key.
  You must identify anomalies in key names as well (for example, if the webhook has "time_stamp" instead of "timestamp")
  Return your answer in the following JSON format:
  {{
    "event_type":"<ExtractedEvent>",
    "timestamp":"<ParsedTimestamp>",
    "source":"<ExtractedSource>",
    "payload":"{{{{<SummarizedPayload>}}}}",
    "anomalies":["<ListofIdentifiedAnomalies>"]
  }}

  ##Examples

  Example1

  Input:
  --------
  {{
  "event_type": "order_created",
  "timestamp": "2025-06-02T10:00:00Z",
  "source": "ecommerce_api",
  "payload": {{
    "order_id": "ORD-10001",
    "user_id": "USR-12345",
    "items": [
      {{
        "item_id": "SKU-001",
        "name": "Phone Case",
        "quantity": 1,
        "unit_price": 9.99
      }}
    ],
    "currency": "USD",
    "total": 9.99,
    "payment_status": "paid",
    "shipping_address": {{
      "name": "Alex Smith",
      "address_line1": "742 Evergreen Terrace",
      "city": "Springfield",
      "postal_code": "62704",
      "country": "USA"
    }}
  }}
  }}
  -------
  Output:
  {{
  "event_type": "order_created",
  "timestamp": "2025-06-02T10:00:00Z",
  "source": "ecommerce_api",
  "payload": "{{order_id: ORD-10001, user_id: USR-12345, total: 9.99, payment_status: paid}}",
  "anomalies": []
  }}
  -------

  Example2

  Input:
  --------
  {{
  "event_type": "order_created",
  "time_stamp": "2025-06-02T10:00:00Z",
  "source": "ecommerce_api",
  "payload": {{
    "order_id": 10001,
    "user_id": "USR-12345",
    "items": [],
    "currency": "USD",
    "total": "9.99",
    "payment_status": "paid",
    "shipping_address": {{
      "name": "Alex Smith",
      "address_line1": "742 Evergreen Terrace",
      "city": "Springfield",
      "postal_code": "62704",
      "country": "USA"
    }}
  }}
  }}
  --------
  Output:
  {{
  "event_type": "order_created",
  "timestamp": null,
  "source": "ecommerce_api",
  "payload": "{{order_id: 10001, user_id: USR-12345, total: 9.99}}",
  "anomalies": [
    "Field 'timestamp' is misspelled as 'time_stamp'",
    "order_id should be a string, but got integer",
    "total should be a float, but got string"
  ]
  }}
  -------
  Now analyze the following input:
  --------
  {input_data}
  --------
  Output:
     """
     return PromptTemplate.from_template(template)

  def run(self, input_id, input_data):
    prompt = self.prompt_template.format(input_data=json.dumps(input_data, indent=2))

    try:
      response = self.model.invoke(prompt)
      result = response.content.strip()
      code_fence_pattern = r"```json\s*(\{.*?\})\s*```"
      match = re.search(code_fence_pattern, result, re.DOTALL)
      if match:
          json_str = match.group(1)
      else:
          # fallback: try to extract first JSON object
          json_match = re.search(r"\{.*?\}", result, re.DOTALL)
          if json_match:
              json_str = json_match.group(0)
          else:
              print("No JSON found in LLM response (json).")
              return None
      parsed_result = json.loads(json_str)

      self.db.insert_extracted_info_json(
        input_id=input_id,
        event_type=parsed_result["event_type"],
        timestamp=parsed_result["timestamp"],
        source=parsed_result["source"],
        payload=json.dumps(parsed_result["payload"]),
        anomalies=json.dumps(parsed_result["anomalies"])
      )

      if parsed_result["anomalies"]:
        self.db.insert_agent_action(
            input_id=input_id,
            agent = self.role,
            description = "Identified anomalies",
            action = "log"
        )
        print("Anomalies logged successfully")

      else:
        self.db.insert_agent_action(
            input_id=input_id,
            agent = self.role,
            description = "No anomalies",
            action = "log"
        )
        print("No anomalies to log")
      
      return input_id

    except Exception as e:
        print(f"An error occurred in JsonAgent: {e}")
        return None
