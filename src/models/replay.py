from src.models.user import db
from datetime import datetime

class Replay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Float, default=30.0)  # duração em segundos
    file_size = db.Column(db.Integer)  # tamanho do arquivo em bytes
    status = db.Column(db.String(50), default='saved')  # saved, processing, error
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'timestamp': self.timestamp.isoformat(),
            'duration': self.duration,
            'file_size': self.file_size,
            'status': self.status
        }

