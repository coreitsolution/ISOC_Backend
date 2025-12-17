from db import db
from flask_marshmallow import Marshmallow

ma = Marshmallow(db)

class MqLogsSchema(ma.Schema):
    class Meta:
        fields = ("mq_logs_id", "mq_topic", "mq_message", "created_at")
        
mq_logs_schema = MqLogsSchema(many=True)
