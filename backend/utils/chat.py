import uuid

from google.adk.sessions import BaseSessionService


class ChatUtils:
    def __init__(self, session_service: BaseSessionService) -> None:
        """
        Initialize ChatUtils with a session service.

        Args:
            session_service: An instance of a session service used to manage sessions.

        """
        self.session_service = session_service

    async def get_or_create_session_id(self, session_id: str | None) -> str:
        """
        Get an existing session by ID or create a new one if it does not exist.

        Args:
            session_id: The session ID to fetch or create.

        Returns:
            The session ID.

        """
        if not session_id:
            session_id = str(uuid.uuid4())

        session = await self.session_service.get_session(
            user_id=session_id,
            session_id=session_id,
            app_name="demistify_agent"
        )
        if not session:
            session = await self.session_service.create_session(
                user_id=session_id, session_id=session_id, app_name="demistify_agent"
            )

        return session_id

