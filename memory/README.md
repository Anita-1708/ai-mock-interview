# In-Memory Session Management System

This module provides a lightweight session management system for the AI Mock Interview application. It handles session creation, message history storage, and session summaries using UUID-based session identifiers, with all data stored in memory only.

## Features

- **UUID-based Session IDs**: Each session gets a unique UUID identifier
- **Message History**: Store and retrieve conversation messages with timestamps
- **Session Summaries**: Maintain summaries of conversation sessions
- **In-Memory Storage**: All data is stored in memory during execution
- **Metadata Support**: Store additional session metadata
- **Session Management**: Create, retrieve, update, and delete sessions
- **Memory Management**: Clear all sessions or get session count

## Core Components

### SessionManager Class
The main class that handles all session operations:
- Session creation and deletion
- Message history management
- Summary updates
- In-memory storage only

### Message Class
Represents individual messages in the conversation:
- Timestamp
- Role (user/assistant)
- Content
- Optional metadata

### Type Definitions
- `MessageHistory`: Type definition for message history entries
- `SessionData`: Type definition for complete session data

## Usage

### Basic Usage

```python
from memory.session import (
    create_session,
    add_message,
    get_message_history,
    update_summary,
    get_summary
)

# Create a new session
session_id = create_session(metadata={"user_name": "John Doe"})

# Add messages to the session
add_message(session_id, "user", "Hello, I'm here for my interview.")
add_message(session_id, "assistant", "Welcome! Let's begin.")

# Get message history
history = get_message_history(session_id)
for message in history:
    print(f"[{message.role}] {message.content}")

# Update session summary
update_summary(session_id, "Technical interview with John Doe - discussed Python experience")

# Get session summary
summary = get_summary(session_id)
print(f"Summary: {summary}")
```

### Advanced Usage

```python
from memory.session import (
    SessionManager,
    list_sessions,
    get_session_info,
    delete_session,
    clear_all_sessions,
    get_session_count
)

# Create a custom session manager
session_manager = SessionManager()

# List all sessions
sessions = list_sessions()
for session_id in sessions:
    info = get_session_info(session_id)
    print(f"Session {session_id}: {info['message_count']} messages")

# Get session count
print(f"Active sessions: {get_session_count()}")

# Delete a session
delete_session(session_id)

# Clear all sessions (useful for cleanup)
clear_all_sessions()
```

## API Reference

### Core Functions

#### `create_session(metadata: Optional[Dict[str, Any]] = None) -> str`
Creates a new session and returns the session ID.

**Parameters:**
- `metadata`: Optional dictionary with session metadata

**Returns:**
- Session ID (UUID string)

#### `add_message(session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool`
Adds a message to the session history.

**Parameters:**
- `session_id`: The session ID
- `role`: Message role ("user" or "assistant")
- `content`: Message content
- `metadata`: Optional message metadata

**Returns:**
- `True` if successful, `False` if session not found

#### `get_message_history(session_id: str) -> List[Message]`
Retrieves the message history for a session.

**Parameters:**
- `session_id`: The session ID

**Returns:**
- List of Message objects

#### `update_summary(session_id: str, summary: str) -> bool`
Updates the session summary.

**Parameters:**
- `session_id`: The session ID
- `summary`: The summary text

**Returns:**
- `True` if successful, `False` if session not found

#### `get_summary(session_id: str) -> Optional[str]`
Retrieves the session summary.

**Parameters:**
- `session_id`: The session ID

**Returns:**
- Summary text or `None` if not found

#### `list_sessions() -> List[str]`
Lists all session IDs.

**Returns:**
- List of session IDs

#### `get_session_info(session_id: str) -> Optional[Dict[str, Any]]`
Gets basic session information.

**Parameters:**
- `session_id`: The session ID

**Returns:**
- Dictionary with session info or `None` if not found

#### `delete_session(session_id: str) -> bool`
Deletes a session from memory.

**Parameters:**
- `session_id`: The session ID

**Returns:**
- `True` if successful, `False` if session not found

#### `clear_all_sessions()`
Clears all sessions from memory.

#### `get_session_count() -> int`
Gets the total number of active sessions.

**Returns:**
- Number of active sessions

### SessionManager Class Methods

The `SessionManager` class provides the same functionality as the global functions, with additional features:

- **Direct access**: Use the manager instance directly instead of global functions
- **Batch operations**: Perform multiple operations efficiently
- **Memory management**: Clear all sessions or get session count

## Data Structure

Sessions are stored in memory with the following structure:

```python
{
    "session_id": "uuid-string",
    "created_at": "2024-01-01T12:00:00",
    "last_updated": "2024-01-01T12:30:00",
    "message_history": [
        {
            "timestamp": "2024-01-01T12:00:00",
            "role": "user",
            "content": "Hello",
            "metadata": null
        }
    ],
    "summary": "Session summary text",
    "metadata": {
        "user_name": "John Doe",
        "interview_type": "technical"
    }
}
```

## Error Handling

The system includes robust error handling:
- Graceful handling of missing sessions
- Type safety with TypedDict definitions
- Automatic timestamp generation

## Performance Considerations

- All data is stored in memory for fast access
- No file I/O operations
- Sessions are automatically cleared when the application stops
- Memory usage scales with the number of sessions and messages
- Consider implementing session cleanup for long-running applications

## Memory Management

Since all data is stored in memory, consider these practices:

- **Session Cleanup**: Use `clear_all_sessions()` when appropriate
- **Session Limits**: Monitor session count with `get_session_count()`
- **Application Restart**: All data is lost when the application restarts
- **Memory Monitoring**: Monitor memory usage for applications with many sessions

## Example

Run the example script to see the system in action:

```bash
python example_usage.py
```

This will demonstrate all the key features of the in-memory session management system.

## Integration with FastAPI

You can easily integrate this with your FastAPI application:

```python
from fastapi import FastAPI
from memory.session import create_session, add_message, get_message_history

app = FastAPI()

@app.post("/start-interview")
async def start_interview(user_name: str):
    session_id = create_session(metadata={"user_name": user_name})
    return {"session_id": session_id}

@app.post("/send-message/{session_id}")
async def send_message(session_id: str, message: str):
    add_message(session_id, "user", message)
    # Process with AI and add response
    ai_response = "AI response here"
    add_message(session_id, "assistant", ai_response)
    return {"response": ai_response}
``` 