from .db import DB
import sqlite3

def view_agent_chain(input_id: int):
    db = DB() 

    query = """
        SELECT agent, description, action, timestamp
        FROM agent_actions
        JOIN metadata ON agent_actions.input_id = metadata.input_id
        WHERE agent_actions.input_id = ?
        ORDER BY agent_actions.id ASC
    """

    db.cursor.execute(query, (input_id,))
    rows = db.cursor.fetchall()

    if not rows:
        print(f"No actions found for input ID: {input_id}")
        return

    print(f"\n=== Agent Chain for Input ID: {input_id} ===\n")
    for idx, (agent, description, action, timestamp) in enumerate(rows, 1):
        print(f"{idx}. Agent: {agent}")
        print(f"   Description: {description}")
        print(f"   Action: {action}")
        print(f"   Timestamp: {timestamp}")
        print("--------------------------------------------")
