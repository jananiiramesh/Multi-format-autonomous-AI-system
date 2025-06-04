from memory.db import DB
from agents.basicAgent import BasicAgent
from langchain_core.prompts import PromptTemplate
import re
import json
from langchain_core.tools import tool
from PyPDF2 import PdfReader
import io
import requests

@tool
def pdf_parser(file_bytes: bytes) -> str:
  """
  Extracting text from a PDF file using PdfReader
  Input: file_bytes - raw PDF bytes
  """
  try:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
      text += page.extract_text() or ""
    return text.strip()
  except Exception as e:
    print(f"An error occurred in pdf_parser: {e}")
    return None
  
class PdfAgent(BasicAgent):
  def __init__(self, input_data=None, role=None, extra_info=None):
    super().__init__(input_data=input_data, role="PdfAgent")
    self.db = DB()

  def create_prompt_template(self):
     template = """
     You are a smart pdf analyzer.
     When given parsed pdf text, you must check for the following details:
     1. Classify whether the pdf is an **invoice** or a **policy/legal document**, or **unknown**
     2. If it is an invoice, then look for the **total amount**. If the total amount is greater than 10,000 then flag it as "High Invoice". Otherwise flag it as "Low Invoice"
     3. If it is a policy/legal document, check for the given flagged terms: GDPR, HIPAA, FDA, PCI-DSS, CCPA, COPPA, COPMC
        If any of the flagged terms are present, flag as "sensitive content", else flag as "non sensitive content"
     4. Lastly, identify the sender (if its an invoice, get the customer's name or if its a policy, get the organization name)

     Return your output as structured JSON:
     {{
        "doc_type":"<invoiceorpolicy>",
        "flagged_keywords":"<identifiedflagsfordoctype>"
        "sender":"<customerororganizationname>"
     }}

     Here is the extracted text:
     -----------------------------------
     {pdf_text}
     -----------------------------------

     """
     return PromptTemplate.from_template(template)

  def run(self, input_id, file_bytes: bytes):
    try:
      pdf_text = pdf_parser.invoke({"file_bytes":file_bytes})
    except Exception as e:
      print(f"Error using pdf_parser tool: {e}")
      return None

    if not pdf_text:
      print("No text extracted from PDF.")
      return None

    prompt = self.prompt_template.format(pdf_text=pdf_text)

    try:
      response = self.model.invoke(prompt)
      result = response.content.strip()

      match = re.search(r"\{.*\}", result, re.DOTALL)
      if not match:
          print("No JSON found in result.")
          return None

      parsed_result = json.loads(match.group(0))

      self.db.insert_extracted_info_pdf(
          input_id=input_id,
          doc_type=parsed_result["doc_type"],
          flags=parsed_result["flagged_keywords"]
      )
      print(f"Inserted extracted_pdf with input_id: {input_id}")

      if parsed_result["doc_type"] == "invoice":
        if parsed_result["flagged_keywords"] == "High Invoice":
          self.db.insert_agent_action(
              input_id=input_id,
              agent = self.role,
              description = "Identified high invoice",
              action = "escalate"
          )
          payload = {
            "source": parsed_result["sender"],
            "issue_id": input_id,
            "message": parsed_result["flagged keywords"],
            "details": "Invoice greater than 10,000"
          }
          try:
            response = requests.post("http://localhost:8000/risk_alert", json=payload)
            ##print(f"Escalation response: {response.status_code} - {response.text}")
            print("Alert sent successfully!")
          except Exception as e:
            print(f"Failed to send alert: {e}")
        else:
          self.db.insert_agent_action(
              input_id=input_id,
              agent = self.role,
              description = "Identified low invoice",
              action = "log"
          )

      else:
        if parsed_result["flagged_keywords"] == "sensitive content":
          self.db.insert_agent_action(
              input_id=input_id,
              agent = self.role,
              description = "Identified sensitive content",
              action = "escalate"
          )
          payload = {
            "source": parsed_result["sender"],
            "issue_id": input_id,
            "message": parsed_result["flagged keywords"],
            "details": "Sensitive words found"
          }
          try:
            response = requests.post("http://localhost:8000/risk_alert", json=payload)
            ##print(f"Escalation response: {response.status_code} - {response.text}")
            print("Alert sent successfully!")
          except Exception as e:
            print(f"Failed to send alert: {e}")
        else:
          self.db.insert_agent_action(
              input_id=input_id,
              agent = self.role,
              description = "Identified non sensitive content",
              action = "log"
          )
          print("Non sensitive content logged")
      return input_id

    except Exception as e:
      print(f"An error occurred in PdfAgent: {e}")
      return None
