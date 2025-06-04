# 🧠 Multi-Format Autonomous Intake & Routing System

This project is a modular, agent-based AI system designed to intelligently process incoming data of multiple formats — Email, JSON Webhook, and PDF. It performs format classification, intent extraction, information parsing, and autonomous action routing based on content.

# 🚀 Tools used
1. Langchain (for prompt templates, ChatGroq for models, only used free apis)
   - Model used: **gemma2-9b-it**
2. Sqlite3 (for shared database, each agents stores its outcomes as well as its next action)
3. FASTAPI
4. PyPDF2

## 🚀 Core Workflow
1. **Input Intake**
   - Accepts emails, json webhooks and pdfs as input. Pass the input into the input variable of agents_routing.py.
   - This input is passed to the FormatClassifierAgent. Uses prompts and few shot classification.
   - Note: To use example files instead of raw email/raw json, a small logic has been applied before passing raw input data to the FormatClassifier, which checks the file
     extension (whether its .txt, .json, .pdf). This logic is implemented only to show the working of the system with the sample input files given in the **inputs** folder.
     According to the extension, raw data is extracted and this data is passed to the FormatClassifier. In practice, the raw data will be directly given to the input
     variable, it won't be part of a file.
     
2. **Format Classifier Agent**
   - This is the actual brain of the system. This agent inherits basic functionalities from the **BasicAgent**, and the methods are overridden with its own logic. With the
     help of a suitable prompt, the agent is made to act like a **intelligent input format and intent classifier**.
   - The agent analyzes the input carefully and determines whether the given data is an email, json, or pdf. It further classifies the business intent (mainly for emails).
   - It returns the format and intent in the form of a json object. This output is stored in the **shared_memory.db** in a table called **metadata**.
   - Finally, based the format it identified, it calls the run() method of the next respective agent (calls run() of EmailAgent if it identifies it as an email). Additionally it also sends the input_id generated while inserting into database to keep track of the chain of events.
     
3. **Email Agent**
   - A specialized prompt was given to this agent to make it act like an email analyszer. This agents extracts details about the sender, how urgent the message is, the subject of the email, the tone of the sender. Based on all these extracted details, the agent needs to make a decision of whether to escalate the issue or mark it as routine
   - The agent follows few shot classification, so two examples were given to help the agent understand better
   - the output of the agent is in json form and is parsed and stored in the shared_memory.db in a separate table called **extracted_info_email**. Along with that the agents decision (escalate/routine) is also stored in a table called **agent_actions**.
   - If the agent declares the message to be escalated, a payload is generated and a post request is sent to /escalate api endpoint. If not, it is simply logged into the memeory

4. **JSON Agent**
   - This agent too was given a specialized prompt to make it a anomaly detector of the json payload. If the schema doesn't match the example schema given in the prompt, or if there is a type error, these are stored in the **extracted_info_json** table, to make it easy to access for analysis.
   - This agent too uses few shot classification. Key requirements like the event_type, timestamp, source, payload (payload is summarized smartly by the agent) are extract and stored. If anomalies are found, it is further logged in the **agent_actions** table

5. **PDF Agent**
   - This agent, apart from having a smart prompt, also uses a specially defined tool called **pdf_parser**. pdf_parser uses the PyPDF2 library to parse the input pdf, as a first step to the extraction process. This tool is called by the PdfAgent's run() method, prior to executing the prompt.
   - The agents, using the smart prompt, is prompted to classify whether the given pdf is and invoice or a policy/legal document. After identification, the agent further checks for two parameters - if it is an invoice, check if the total amount is greater than 10000 or if its a policy, check if there are sensitive words (like GDPR, HIPAA, FDA, etc). All the sensitive words to look out for were specified in the prompt
   - The extracted doc_type and flags are in json format and are stored in the **extracted_info_pdf** with the input_id from formatclassifier as the foreign key.
   - In case, a flag of "high invoice" or "sensitive content" is raised (while analysis), a request is sent to the /risk_alert api endpoint, sending a payload with the details.
   - These further actions are logged in the **agent_actions** table with the help of the input_id.
  
6. **Shared Database**
   - All agents have an attribute **db** which had a common instance of the database, a singleton instance. So all the data logged by each agent is accessible to the other. This singleton instance allows each agent to individually log its actions, and can later be joined by input_id to display the chain of actions (which is exhibited by the view_action_chain() in the see_action_chain.py)
   - The shared_memory.db has the following tables: metadata (populated by FCAgent), extracted_info_email (populated by EmailAgent), extracted_info_json (populated by JsonAgent), extracted_info_pdf (populated by PdfAgent), agent_actions(populated by all agents - logging what input they got and what is the next agent they're passing it to), routine_log (populated only by EmailAgent when it receives a routine email).
   - All the tables have a common foreign key, input_id, to keep track of each particular input in the chain.

7. **API Endpoints**
   - Uses FastAPI, two endpoints namely /escalate and /risk_alert and defined.
