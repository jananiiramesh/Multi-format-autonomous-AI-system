from memory.db import DB
from agents.basicAgent import BasicAgent
from langchain_core.prompts import PromptTemplate
from agents.emailAgent import EmailAgent
from agents.jsonAgent import JsonAgent
from agents.pdfAgent import PdfAgent
import re
import json

class FormatClassifierAgent(BasicAgent):
  def __init__(self, input_data=None, role=None, extra_info=None):
    super().__init__(input_data=input_data, role="FormatClassifier")
    self.db = DB()

  def create_prompt_template(self):
    template = """
    You are an intelligent input format classifier.
    You must analyze the provided data and identify its format as one of the following:
    - Email
    - JSON
    - PDF
    Along with this, you must also identify the intent of the text as one of the following (strictly classify the intent among these 5 options only, if it doesn't match, find the closest category):
    - RFQ (Request for Quotation)
    - Complaint
    - Invoice
    - Regulation
    - Fraud
    Return your answer in the following JSON format:
    {{
      "format":"<PredictedFormat>",
      "intent":"<PredictedIntent>"
    }}

    ## Examples

    Example1

    Input:
    -----
    Subject: Request for Quotation

    Hello team,

    We are interested in purchasing 200 units of your product. Please share a quotation for the same.

    Thanks,
    XYZ Team

    -----
    Output:
    {{
      "format":"Email",
      "intent":"RFQ"
    }}
    -------
    Example 2

    Input:
    ------
    {{
      "type":"invoice",
      "client":"ABC limited",
      "amount": 1200,
      "due":"12-06-2025"
    }}
    -----
    Output:
    {{
      "format":"JSON",
      "intent":"Invoice"
    }}
    -------

    ### Now analyze the following input:
    -----
    {input_data}
    -----
    Output:


    """
    return PromptTemplate.from_template(template)

  def run(self):
    prompt = self.prompt_template.format(input_data = self.input_data)

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
              print("No JSON found in LLM response.")
              return None

      parsed_result = json.loads(json_str)

      input_id = self.db.insert_metadata(
        format_=parsed_result["format"],
        intent=parsed_result["intent"]
      )
      print("Input passed with input_id ",input_id)
      format_ = parsed_result["format"].lower()

      if format_ == "email":
        self.db.insert_agent_action(
            input_id=input_id,
            agent = self.role,
            description = "Idenitfied email format",
            action = "EmailAgent"
        )
        return EmailAgent().run(input_id, self.input_data)
      elif format_ == "json":
        self.db.insert_agent_action(
            input_id=input_id,
            agent = self.role,
            description = "Idenitfied json format",
            action = "JsonAgent"
        )
        return JsonAgent().run(input_id, self.input_data)
      elif format_ == "pdf":
        self.db.insert_agent_action(
            input_id=input_id,
            agent = self.role,
            description = "Idenitfied pdf format",
            action = "PdfAgent"
        )
        try:
          file_bytes = self.input_data.read()

          return PdfAgent().run(input_id, file_bytes)

        except Exception as e:
          print(f"Error reading uploaded PDF file: {e}")
          return None
        return PdfAgent().run(input_id, self.input_data)
      else:
            print(f"Unknown format '{format_}'. Cannot route.")
            return None

    except Exception as e:
        print(f"An error occurred in FormatClassifierAgent: {e}")
        return None
