# 🧠 Multi-Format Autonomous Intake & Routing System

This project is a modular, agent-based AI system designed to intelligently process incoming data of multiple formats — Email, JSON Webhook, and PDF. It performs format classification, intent extraction, information parsing, and autonomous action routing based on content.

# 🚀 Tools used
1. Langchain (for prompt templates, ChatGroq for models, only used free apis)
   - Model used: **gemma2-9b-it**
2. Sqlite3 (for shared database, each agents stores its outcomes as well as its next action)

## 🚀 Core Workflow
1. **Input Intake**
   - Accepts emails, json webhooks and pdfs as input. Pass the input into the input variable of agents_routing.py.
   - This input is passed to the FormatClassifierAgent.
   - Note: To use example files instead of raw email/raw json, a small logic has been applied before passing raw input data to the FormatClassifier, which checks the file
     extension (whether its .txt, .json, .pdf). This logic is implemented only to show the working of the system with the sample input files given in the **inputs** folder.
     According to the extension, raw data is extracted and this data is passed to the FormatClassifier. In practice, the raw data will be directly given to the input
     variable, it won't be part of a file.
2. **Format Classifier Agent**
   - This is the actual brain of the system. This agent inherits basic functionalities from the **BasicAgent**, and the methods are overridden with its own logic. With the
     help of a suitable prompt, the agent is made to act like a **intelligent input format and intent classifier**.
   - The agent analyzes the input carefully and determines whether the given data is an email, json, or pdf. It further classifies the business intent (mainly for emails).
   - It returns the format and intent in the form of a json object. This output is stored in the **shared_memory.db** in a table called **metadata**.
   - Finally, based the format it identified, it calls the run() method of the next respective agent (calls run() of EmailAgent if it identifies it as an email)
3. **Email Agent**
   - 
