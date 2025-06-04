import sqlite3
import threading

class DB:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path="shared_memory.db"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DB, cls).__new__(cls)
                cls._instance.db_path = db_path
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            input_id INTEGER PRIMARY KEY AUTOINCREMENT,
            format TEXT,
            intent TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS extracted_info_email (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_id INTEGER,
            sender TEXT,
            urgency TEXT CHECK(urgency IN ('low', 'medium', 'high')) NOT NULL,
            subject TEXT CHECK(subject IN ('request', 'issue')) NOT NULL,
            tone TEXT,
            FOREIGN KEY(input_id) REFERENCES metadata(id)
            )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS extracted_info_json (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_id INTEGER,
            event_type TEXT,
            timestamp DATETIME,
            source TEXT,
            payload TEXT,
            anomalies TEXT,
            FOREIGN KEY(input_id) REFERENCES metadata(id))
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS extracted_info_pdf (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          input_id INTEGER,
          doc_type TEXT,
          flags TEXT,
          FOREIGN KEY(input_id) REFERENCES metadata(id))
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_id INTEGER,
            agent TEXT,
            description TEXT,
            action TEXT,
            FOREIGN KEY(input_id) REFERENCES metadata(id))
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS routine_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_id INTEGER,
            subject TEXT,
            FOREIGN KEY(input_id) REFERENCES metadata(id))
        """)

        self.conn.commit()

    def insert_metadata(self, format_, intent):
        self.cursor.execute("""
            INSERT INTO metadata (format, intent)
            VALUES (?, ?)
        """, (format_, intent))
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_extracted_info_email(self, input_id, sender, urgency, subject, tone):
        self.cursor.execute("""
            INSERT INTO extracted_info_email (input_id, sender, urgency, subject, tone)
            VALUES (?, ?, ?, ?, ?)
        """, (input_id, sender, urgency, subject, tone))
        self.conn.commit()

    def insert_extracted_info_json(self, input_id, event_type, timestamp, source, payload, anomalies):
        self.cursor.execute("""
            INSERT INTO extracted_info_json (input_id, event_type, timestamp, source, payload, anomalies)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (input_id, event_type, timestamp, source, payload, anomalies))
        self.conn.commit()

    def insert_extracted_info_pdf(self, input_id, doc_type, flags):
      self.cursor.execute("""
          INSERT INTO extracted_info_pdf (input_id, doc_type, flags)
          VALUES (?, ?, ?)
      """, (input_id, doc_type, flags))
      self.conn.commit()

    def insert_agent_action(self, input_id, agent, description, action):
        self.cursor.execute("""
            INSERT INTO agent_actions (input_id, agent, description, action)
            VALUES (?, ?, ?, ?)
        """, (input_id, agent, description, action))
        self.conn.commit()

    def insert_routine_log(self, input_id, subject):
        self.cursor.execute("""
            INSERT INTO routine_log (input_id, subject)
            VALUES (?, ?)
        """, (input_id, subject))
        self.conn.commit()

    def close(self):
        self.conn.close()
