import json
import logging
import re

from google.adk.runners import Runner
from google.adk.sessions import BaseSessionService
from google.genai import types

from agent import metadata_agent

logger = logging.getLogger(__name__)


class MetadataUtils:
    @staticmethod
    async def extract_metadata(header_content: str, session_id: str, session_service: BaseSessionService) -> dict:
        """
        Extract metadata from the given header content using the metadata agent.

        This method sends the header content to the metadata agent, waits for
        the final response, parses it, and returns the metadata as a dictionary.

        Args:
            header_content: The raw content (string) from which to extract metadata.
            session_id: The unique session ID for this request.
            session_service: The session service used to manage user sessions.

        Returns:
            A dictionary containing the extracted metadata. Returns an empty
            dictionary if no valid metadata is found.

        """
        agent = metadata_agent()

        metadata_agent_content = types.Content(role="user", parts=[types.Part(text=header_content)])
        metadata_agent_runner = Runner(agent=agent, app_name="demistify_agent", session_service=session_service)

        logger.info("Running metadata agent...")

        metadata_data = "No final response received."
        async for event in metadata_agent_runner.run_async(
            user_id=session_id, session_id=session_id, new_message=metadata_agent_content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                content = event.content.parts[0]
                metadata_data = content.text if content.text else "No final response received."

        logger.info("Metadata agent response: %s", metadata_data)
        match = re.search(r"\{.*\}", metadata_data, re.DOTALL)
        metadata = {}
        if match:
            clean = match.group(0)
            metadata = json.loads(clean)

        return metadata
