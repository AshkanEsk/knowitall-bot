"""User session management for mode tracking."""

from config.settings import BotMode


class UserSession:
    """Manages user session data including current mode."""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.mode: BotMode = BotMode.DICTIONARY
    
    def set_mode(self, mode: BotMode) -> None:
        """Set the bot mode for this user."""
        self.mode = mode
    
    def get_mode(self) -> BotMode:
        """Get current bot mode."""
        return self.mode


class SessionManager:
    """Manages all user sessions."""
    
    def __init__(self):
        self._sessions: dict[int, UserSession] = {}
    
    def get_session(self, user_id: int) -> UserSession:
        """Get or create session for user."""
        if user_id not in self._sessions:
            self._sessions[user_id] = UserSession(user_id)
        return self._sessions[user_id]
    
    def clear_session(self, user_id: int) -> None:
        """Clear user session."""
        self._sessions.pop(user_id, None)