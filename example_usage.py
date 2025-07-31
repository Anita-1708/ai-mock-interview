#!/usr/bin/env python3
"""
Example usage of the in-memory session management system
"""

from memory.session import (
    create_session, 
    add_message, 
    get_message_history, 
    update_summary, 
    get_summary,
    list_sessions,
    get_session_info,
    delete_session,
    clear_all_sessions,
    get_session_count
)


def main():
    """Demonstrate in-memory session management functionality"""
    
    print("=== In-Memory Session Management Example ===\n")
    
    # Create a new session
    print("1. Creating a new session...")
    session_id = create_session(metadata={"user_name": "John Doe", "interview_type": "technical"})
    print(f"   Session created with ID: {session_id}")
    print(f"   Active sessions: {get_session_count()}\n")
    
    # Add some messages to the session
    print("2. Adding messages to the session...")
    add_message(session_id, "user", "Hello, I'm here for my technical interview.")
    add_message(session_id, "assistant", "Welcome! I'm your AI interviewer. Let's start with some basic questions.")
    add_message(session_id, "user", "Sure, I'm ready.")
    add_message(session_id, "assistant", "Great! Can you tell me about your experience with Python?")
    add_message(session_id, "user", "I have 3 years of experience with Python, mostly in web development and data analysis.")
    print("   Messages added successfully!\n")
    
    # Get message history
    print("3. Retrieving message history...")
    history = get_message_history(session_id)
    for i, message in enumerate(history, 1):
        print(f"   {i}. [{message.role}] {message.content}")
    print()
    
    # Update session summary
    print("4. Updating session summary...")
    summary = "Technical interview session with John Doe. Discussed Python experience (3 years, web dev & data analysis). Session is ongoing."
    update_summary(session_id, summary)
    print("   Summary updated!\n")
    
    # Get session summary
    print("5. Retrieving session summary...")
    retrieved_summary = get_summary(session_id)
    print(f"   Summary: {retrieved_summary}\n")
    
    # Get session information
    print("6. Getting session information...")
    session_info = get_session_info(session_id)
    if session_info:
        print(f"   Session ID: {session_info['session_id']}")
        print(f"   Created: {session_info['created_at']}")
        print(f"   Last Updated: {session_info['last_updated']}")
        print(f"   Message Count: {session_info['message_count']}")
        print(f"   Has Summary: {session_info['has_summary']}")
        print(f"   Metadata: {session_info['metadata']}")
    print()
    
    # List all sessions
    print("7. Listing all sessions...")
    sessions = list_sessions()
    print(f"   Total sessions: {len(sessions)}")
    for sid in sessions:
        print(f"   - {sid}")
    print()
    
    # Create another session to demonstrate multiple sessions
    print("8. Creating another session...")
    session_id_2 = create_session(metadata={"user_name": "Jane Smith", "interview_type": "behavioral"})
    print(f"   Second session created: {session_id_2}")
    add_message(session_id_2, "user", "Hi, I'm Jane. I'm here for my behavioral interview.")
    add_message(session_id_2, "assistant", "Hello Jane! Let's talk about your work experience.")
    print(f"   Messages added to second session!")
    print(f"   Active sessions: {get_session_count()}\n")
    
    # List sessions again
    print("9. Updated session list...")
    sessions = list_sessions()
    print(f"   Total sessions: {len(sessions)}")
    for sid in sessions:
        info = get_session_info(sid)
        if info:
            print(f"   - {sid} ({info['message_count']} messages)")
    print()
    
    # Clean up - delete the second session
    print("10. Cleaning up - deleting second session...")
    delete_session(session_id_2)
    print("   Second session deleted!")
    print(f"   Active sessions: {get_session_count()}")
    
    # Final session list
    print("\n11. Final session list...")
    sessions = list_sessions()
    print(f"   Total sessions: {len(sessions)}")
    for sid in sessions:
        print(f"   - {sid}")
    
    # Demonstrate clearing all sessions
    print("\n12. Clearing all sessions...")
    clear_all_sessions()
    print(f"   All sessions cleared!")
    print(f"   Active sessions: {get_session_count()}")
    
    print("\n=== Example completed! ===")
    print("Note: All session data was stored in memory only and is now cleared.")


if __name__ == "__main__":
    main() 