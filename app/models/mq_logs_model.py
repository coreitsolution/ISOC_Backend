from db import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as sa_text

class MqLogsModel(db.Model):
    __tablename__ = "mq_logs"

    mq_logs_id = db.Column(UUID(
        as_uuid=True), primary_key=True, server_default=sa_text("uuid_generate_v4()"))
    mq_topic = db.Column(db.String(255), nullable=False)
    mq_message = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, server_default=sa_text("CURRENT_TIMESTAMP"), nullable=False)
    
    def __init__(self, mq_topic, mq_message):
        self.mq_topic = mq_topic
        self.mq_message = mq_message
    