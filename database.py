"""
Database module for storing conversation history
Compatible with Python 3.13+
"""
try:
    from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

from datetime import datetime
import json
import pickle
import os
from pathlib import Path

# Fallback to simple file-based database if SQLAlchemy not available
if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()
    
    class Conversation(Base):
        __tablename__ = 'conversations'
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        title = Column(String(200))
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        model = Column(String(100))
        messages_json = Column(Text)
        message_count = Column(Integer, default=0)


class Database:
    """Database handler with fallback support"""
    
    def __init__(self, db_path="conversations.db"):
        self.db_path = db_path
        self.use_sqlalchemy = SQLALCHEMY_AVAILABLE
        
        if self.use_sqlalchemy:
            try:
                self._init_sqlalchemy(db_path)
            except Exception as e:
                print(f"SQLAlchemy initialization failed: {e}")
                print("Falling back to file-based storage...")
                self.use_sqlalchemy = False
                self._init_file_based()
        else:
            self._init_file_based()
    
    def _init_sqlalchemy(self, db_path):
        """Initialize SQLAlchemy database"""
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def _init_file_based(self):
        """Initialize simple file-based storage"""
        self.data_dir = Path("conversation_data")
        self.data_dir.mkdir(exist_ok=True)
        self.index_file = self.data_dir / "index.json"
        
        # Load or create index
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.conversations = json.load(f)
        else:
            self.conversations = {}
            self._save_index()
    
    def _save_index(self):
        """Save conversation index"""
        with open(self.index_file, 'w') as f:
            json.dump(self.conversations, f, indent=2)
    
    def _get_next_id(self):
        """Get next available conversation ID"""
        if not self.conversations:
            return 1
        return max(int(k) for k in self.conversations.keys()) + 1
    
    def create_conversation(self, title, model):
        """Create a new conversation"""
        if self.use_sqlalchemy:
            conv = Conversation(
                title=title,
                model=model,
                messages_json=json.dumps([]),
                message_count=0
            )
            self.session.add(conv)
            self.session.commit()
            return conv.id
        else:
            conv_id = str(self._get_next_id())
            self.conversations[conv_id] = {
                'id': int(conv_id),
                'title': title,
                'model': model,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'message_count': 0,
                'messages': []
            }
            self._save_index()
            return int(conv_id)
    
    def update_conversation(self, conv_id, messages):
        """Update conversation with new messages"""
        if self.use_sqlalchemy:
            conv = self.session.query(Conversation).filter_by(id=conv_id).first()
            if conv:
                conv.messages_json = json.dumps(messages)
                conv.message_count = len(messages)
                conv.updated_at = datetime.utcnow()
                self.session.commit()
                return True
            return False
        else:
            conv_id_str = str(conv_id)
            if conv_id_str in self.conversations:
                self.conversations[conv_id_str]['messages'] = messages
                self.conversations[conv_id_str]['message_count'] = len(messages)
                self.conversations[conv_id_str]['updated_at'] = datetime.utcnow().isoformat()
                self._save_index()
                return True
            return False
    
    def get_conversation(self, conv_id):
        """Get a specific conversation"""
        if self.use_sqlalchemy:
            conv = self.session.query(Conversation).filter_by(id=conv_id).first()
            if conv:
                return {
                    'id': conv.id,
                    'title': conv.title,
                    'created_at': conv.created_at,
                    'updated_at': conv.updated_at,
                    'model': conv.model,
                    'messages': json.loads(conv.messages_json),
                    'message_count': conv.message_count
                }
            return None
        else:
            conv_id_str = str(conv_id)
            if conv_id_str in self.conversations:
                conv = self.conversations[conv_id_str].copy()
                # Convert ISO strings back to datetime objects for consistency
                conv['created_at'] = datetime.fromisoformat(conv['created_at'])
                conv['updated_at'] = datetime.fromisoformat(conv['updated_at'])
                return conv
            return None
    
    def get_all_conversations(self):
        """Get all conversations, sorted by most recent"""
        if self.use_sqlalchemy:
            convs = self.session.query(Conversation).order_by(Conversation.updated_at.desc()).all()
            return [{
                'id': c.id,
                'title': c.title,
                'created_at': c.created_at,
                'updated_at': c.updated_at,
                'model': c.model,
                'message_count': c.message_count
            } for c in convs]
        else:
            convs = []
            for conv_id, conv_data in self.conversations.items():
                convs.append({
                    'id': conv_data['id'],
                    'title': conv_data['title'],
                    'created_at': datetime.fromisoformat(conv_data['created_at']),
                    'updated_at': datetime.fromisoformat(conv_data['updated_at']),
                    'model': conv_data['model'],
                    'message_count': conv_data['message_count']
                })
            # Sort by updated_at descending
            convs.sort(key=lambda x: x['updated_at'], reverse=True)
            return convs
    
    def delete_conversation(self, conv_id):
        """Delete a conversation"""
        if self.use_sqlalchemy:
            conv = self.session.query(Conversation).filter_by(id=conv_id).first()
            if conv:
                self.session.delete(conv)
                self.session.commit()
                return True
            return False
        else:
            conv_id_str = str(conv_id)
            if conv_id_str in self.conversations:
                del self.conversations[conv_id_str]
                self._save_index()
                return True
            return False
    
    def search_conversations(self, query):
        """Search conversations by title or content"""
        query_lower = query.lower()
        
        if self.use_sqlalchemy:
            convs = self.session.query(Conversation).filter(
                (Conversation.title.contains(query)) | 
                (Conversation.messages_json.contains(query))
            ).order_by(Conversation.updated_at.desc()).all()
            
            return [{
                'id': c.id,
                'title': c.title,
                'created_at': c.created_at,
                'updated_at': c.updated_at,
                'model': c.model,
                'message_count': c.message_count
            } for c in convs]
        else:
            results = []
            for conv_id, conv_data in self.conversations.items():
                # Search in title
                if query_lower in conv_data['title'].lower():
                    results.append({
                        'id': conv_data['id'],
                        'title': conv_data['title'],
                        'created_at': datetime.fromisoformat(conv_data['created_at']),
                        'updated_at': datetime.fromisoformat(conv_data['updated_at']),
                        'model': conv_data['model'],
                        'message_count': conv_data['message_count']
                    })
                    continue
                
                # Search in messages
                messages_str = json.dumps(conv_data['messages']).lower()
                if query_lower in messages_str:
                    results.append({
                        'id': conv_data['id'],
                        'title': conv_data['title'],
                        'created_at': datetime.fromisoformat(conv_data['created_at']),
                        'updated_at': datetime.fromisoformat(conv_data['updated_at']),
                        'model': conv_data['model'],
                        'message_count': conv_data['message_count']
                    })
            
            # Sort by updated_at descending
            results.sort(key=lambda x: x['updated_at'], reverse=True)
            return results
