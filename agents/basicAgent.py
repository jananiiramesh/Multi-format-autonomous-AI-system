from dotenv import load_dotenv
import os
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
langchain_project = os.getenv("LANGCHAIN_PROJECT")

llm = ChatGroq(groq_api_key=groq_api_key, model_name="gemma2-9b-it")

class BasicAgent:
  def __init__(self, input_data=None, role=None, extra_info=None):
    self.input_data = input_data
    self.role = role
    self.extra_info = extra_info
    self.prompt_template = self.create_prompt_template()
    self.model = llm

  def create_prompt_template(self):
    raise NotImplementedError("Subclasses must implement this method.")

  def run(self):
    prompt = self.prompt_template.format(input_data=self.input_data)
    try:
      response = self.model.invoke(prompt)
      return response.content
    except Exception as e:
      print(f"An error occurred: {e}")
      return None

  def _format_input(self):
    return {"input_data": self.input_data, **self.extra_info}
