from memory.db import DB
from agents.basicAgent import BasicAgent
from langchain_core.prompts import PromptTemplate
import re
import json
import requests

class EmailAgent(BasicAgent):
  def __init__(self, input_data=None, role=None, extra_info=None):
    super().__init__(input_data=input_data, role="EmailAgent")
    self.db = DB()

  def create_prompt_template(self):
     template = """"
     You are an Email analyzer.
     When given an input email, you must carefully assess the following parts:
     1. Sender (who is the email from)
     2. Urgency (based on the email content, classify the urgency of the issue or request as low, medium or high)
     3. Subject (based on content, classify subject as either request or issue)
     4. Tone (the tone of the content, e.g escalation, polite, threatening, etc.)
     5. Whether is its a situation that requires escalation (for example, complaints, service outages, deadline pressure, and anything which requires immediate action or is highly urgent), in which case you must return escalate. 
        If not, identify if its a routine task (for example, placing orders, general inquiries, new requests, or anything that's not urgent), in which case you must return routine
        If it falls under neither (for example, a good review email), mark the field as None
     Return the your answer in the following JSON format:
     {{
        "sender":"<IdentifiedSender>",
        "urgency":"<PredictedUrgency>",
        "subject":"<PredictedClassification>",
        "tone":"<PredictedTone>"
        "action":"<EscalationRoutineOrNone>"
     }}

     ##Examples

     Example1

     Input:
     -----
     Subject: Utterly Disappointed with Your Service

    Hello team,

    Honestly, this has been the worst experience I’ve had with any company. Your team messed up my order completely and I’ve wasted hours trying to get someone to fix it. I expect this to be resolved immediately, or I’ll take my business elsewhere.

    Thanks,
    Mr abc

    -----
    Output:
    {{
      "sender":"Mr abc",
      "urgency":"high",
      "subject":"issue",
      "tone":"rude"
      "action":"escalate"
    }}
    -------

    Example2

     Input:
     -----
     Subject: Request for Product Quotation

    Dear Team,

    I hope this message finds you well.
    We are exploring procurement options for our upcoming project and are very interested in your offerings.
    Could you kindly provide a quotation for 150 units of your Model X device, including delivery timelines and bulk pricing, if applicable?
    Looking forward to your response

    Thanks,
    Mr xyz

    -----
    Output:
    {{
      "sender":"Mr xyz",
      "urgency":"high",
      "subject":"request",
      "tone":"polite"
      "action":"routine"
    }}
    -------

    Example3

     Input:
     -----
     Subject: Inquiry About Product Availability

    I hope you're doing well. I wanted to check if your Model Z air purifiers will be back in stock anytime soon. There’s no immediate need on our end, but we are planning for a possible bulk order later this quarter.
    Would appreciate it if you could share availability details whenever convenient.

    Thanks,
    Mr J

    -----
    Output:
    {{
      "sender":"Mr J",
      "urgency":"low",
      "subject":"request",
      "tone":"polite"
      "action":"routine"
    }}
    -------
    ### Now analyze the following input:
    -----
    {input_data}
    -----
    Output:

     """
     return PromptTemplate.from_template(template)

  def run(self, input_id, input_data):
    prompt = self.prompt_template.format(input_data = input_data)
    #print(prompt)

    try:
      response = self.model.invoke(prompt)
      result = response.content.strip()
      #print(result)
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
              print("No JSON found in LLM response (email).")
              return None
      parsed_result = json.loads(json_str)
      #print(parsed_result)

      self.db.insert_extracted_info_email(
        input_id=input_id,
        sender=parsed_result["sender"],
        urgency=parsed_result["urgency"],
        subject=parsed_result["subject"],
        tone=parsed_result["tone"]
      )

      if parsed_result['action'] == "escalate":
        self.db.insert_agent_action(
            input_id=input_id,
            agent = self.role,
            description = "Identified high urgency",
            action = "Escalate"
        )
        payload = {
        "source": parsed_result["sender"],
        "issue_id": input_id,
        "message": parsed_result["subject"],
        "details": "High urgency email detected and escalated."
        }
        try:
          response = requests.post("http://localhost:8000/escalate", json=payload)
          ##print(f"Escalation response: {response.status_code} - {response.text}")
          print("Issue escalated successfully!")
        except Exception as e:
          print(f"Failed to escalate issue: {e}")

      elif parsed_result['action'] == "routine":
        self.db.insert_agent_action(
            input_id=input_id,
            agent = self.role,
            description = "Identified low urgency",
            action = "Log"
        )
        self.db.insert_routine_log(
            input_id=input_id,
            subject=parsed_result["subject"]
        )
      else:
        self.db.insert_agent_action(
            input_id=input_id,
            agent = self.role,
            description = "Identified none",
            action = "None"
        )
      return input_id

    except Exception as e:
        print(f"An error occurred in EmailAgent: {e}")
        return None
