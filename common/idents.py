SQLALCHEMY_DATABASE_URL = "sqlite:///../data/sql_app.db"

class TaskStatus:
    PENDING = "p"
    SENT = "s"
    PROBLEM = "b"

class WorkerStatus:
    READY = "r"
    BUSY = "b"