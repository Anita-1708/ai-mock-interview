import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from typing import TypedDict

from enums import Phase


class MessageHistory(TypedDict):
    """Type definition for message history entries"""
    timestamp: str
    role: str  # 'user' or 'assistant'
    content: str
    which_phase : Phase
    metadata: Optional[Dict[str, Any]]


class SessionData(TypedDict,total=False):
    """Type definition for session data"""
    session_id: str
    created_at: str
    last_updated: str
    message_history: List[MessageHistory]
    summary: Optional[str]
    phase : Phase
    metadata: Optional[Dict[str, Any]]


@dataclass
class Message:
    """Represents a single message in the conversation"""
    timestamp: str
    role: str
    content: str
    which_phase : Phase
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> MessageHistory:
        return {
            "timestamp": self.timestamp,
            "role": self.role,
            "content": self.content,
            "which_phase" : self.which_phase,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: MessageHistory) -> 'Message':
        return cls(
            timestamp=data["timestamp"],
            role=data["role"],
            content=data["content"],
            which_phase = data.get("which_phase") or Phase.START,
            metadata=data.get("metadata")
        )


class SessionManager:
    """Manages session creation, storage, and retrieval in memory only"""
    
    def __init__(self):
        self.sessions: Dict[str, SessionData] = {}
    
    def create_session(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new session with a unique UUID"""
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        session_data: SessionData = {
            "session_id": session_id,
            "created_at": now,
            "last_updated": now,
            "message_history": [],
            "summary": None,
            "metadata": metadata or {}
        }
        
        self.sessions[session_id] = session_data
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str, which_phase : Phase,
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a message to the session history"""
        if session_id not in self.sessions:
            return False
        
        message = Message(
            timestamp=datetime.now().isoformat(),
            role=role,
            content=content,
            which_phase=which_phase,
            metadata=metadata
        )
        
        self.sessions[session_id]["message_history"].append(message.to_dict())
        self.sessions[session_id]["last_updated"] = datetime.now().isoformat()
        return True
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session data by session ID"""
        return self.sessions.get(session_id)
    
    def get_message_history(self, session_id: str) -> List[Message]:
        """Get message history for a session"""
        if session_id not in self.sessions:
            return []
        
        history = self.sessions[session_id]["message_history"]
        return [Message.from_dict(msg) for msg in history]
    
    def update_summary(self, session_id: str, summary: str) -> bool:
        """Update the session summary"""
        if session_id not in self.sessions:
            return False
        
        self.sessions[session_id]["summary"] = summary
        self.sessions[session_id]["last_updated"] = datetime.now().isoformat()
        return True
    
    def get_summary(self, session_id: str) -> Optional[str]:
        """Get the session summary"""
        if session_id not in self.sessions:
            return None
        return self.sessions[session_id]["summary"]
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id not in self.sessions:
            return False
        
        # Remove from memory
        del self.sessions[session_id]
        return True
    
    def list_sessions(self) -> List[str]:
        """List all session IDs"""
        return list(self.sessions.keys())
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get basic session information"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        return {
            "session_id": session["session_id"],
            "created_at": session["created_at"],
            "last_updated": session["last_updated"],
            "message_count": len(session["message_history"]),
            "has_summary": session["summary"] is not None,
            "metadata": session["metadata"]
        }
    
    def clear_all_sessions(self):
        """Clear all sessions from memory"""
        self.sessions.clear()
    
    def get_session_count(self) -> int:
        """Get the total number of active sessions"""
        return len(self.sessions)


# Global session manager instance
session_manager = SessionManager()


def create_session(metadata: Optional[Dict[str, Any]] = None) -> str:
    """Create a new session and return the session ID"""
    return session_manager.create_session(metadata)


def add_message(session_id: str, role: str, content: str,which_phase : Phase,
               metadata: Optional[Dict[str, Any]] = None) -> bool:
    """Add a message to a session"""
    return session_manager.add_message(session_id, role, content, which_phase,metadata)

def update_phase(session_id: str, phase: Phase):
    """Update the phase of the session"""
    session_manager.sessions[session_id]["phase"] = phase
    return True


def get_session(session_id: str) -> Optional[SessionData]:
    """Get session data"""
    return session_manager.get_session(session_id)


def flatten_message_history(messages: List[MessageHistory]) -> str:
    return "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages)



def flatten_message_history_based_on_phase(messages: List[MessageHistory], phase_filter: Optional[Phase] = None) -> str:
    filtered_messages = [
        msg for msg in messages
        if phase_filter is None or msg["which_phase"] == phase_filter
    ]
    return "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in filtered_messages)


def get_message_history(session_id: str) -> List[Message]:
    """Get message history for a session"""
    return session_manager.get_message_history(session_id)


def update_summary(session_id: str, summary: str) -> bool:
    """Update session summary"""
    return session_manager.update_summary(session_id, summary)


def get_summary(session_id: str) -> Optional[str]:
    """Get session summary"""
    return session_manager.get_summary(session_id)


def delete_session(session_id: str) -> bool:
    """Delete a session"""
    return session_manager.delete_session(session_id)


def list_sessions() -> List[str]:
    """List all session IDs"""
    return session_manager.list_sessions()


def get_session_info(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session information"""
    return session_manager.get_session_info(session_id)


def clear_all_sessions():
    """Clear all sessions from memory"""
    session_manager.clear_all_sessions()


def get_session_count() -> int:
    """Get the total number of active sessions"""
    return session_manager.get_session_count()
    
    