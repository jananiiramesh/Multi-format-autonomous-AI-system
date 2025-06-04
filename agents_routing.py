import os
import json
from agents.formatClassifierAgent import FormatClassifierAgent
from memory.see_action_chain import view_agent_chain

def load_input(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    elif ext == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    elif ext == ".pdf":
        return open(file_path, "rb")

    else:
        raise ValueError("Unsupported file type")

if __name__ == "__main__":
    file_path = "inputs/example_email.txt"

    input_data = load_input(file_path)
    agent = FormatClassifierAgent(input_data=input_data)
    result_id = agent.run()

    print(f"\nInput ID: {result_id}")
    view_agent_chain(result_id)

    # Clean up file object (if opened)
    if hasattr(input_data, "close"):
        input_data.close()
