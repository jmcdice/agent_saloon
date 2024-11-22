# src/models/title_generator.py

from src.agents.agents import Agents
from src.prompts.title_prompts import ZERO_TITLE_PROMPT, GUSTAVE_TITLE_PROMPT
from src.config import TITLE_GENERATION
from src.utils.irc_logger import irc_logger
import traceback

class TitleGenerator:
    def __init__(self, topic):
        self.topic = topic
        self.agents = Agents()
        self.messages = []
        self.title = None
        self._setup_agents()

    def _setup_agents(self):
        """Initialize the Zero and Gustave agents with title-specific prompts"""
        self.zero_agent = self.agents.get_zero(ZERO_TITLE_PROMPT, self._handoff_to_gustave)
        self.gustave_agent = self.agents.get_gustave(GUSTAVE_TITLE_PROMPT, self._handoff_to_zero)

    def _handoff_to_gustave(self):
        return self.gustave_agent

    def _handoff_to_zero(self):
        return self.zero_agent

    def format_message(self, content):
        """
        Formats the message content by removing system messages and extracting consensus.
        """
        if not isinstance(content, str):
            content = str(content or "")
        lines = []
        consensus = None

        # Split content into lines and process
        for line in content.split('\n'):
            # Skip system messages
            if line.startswith("HANDOFF:") or line.startswith("functions."):
                continue

            # Extract consensus
            if line.startswith("Consensus:"):
                consensus = line.strip()
                continue

            # Extract book title if present
            if line.startswith("Book Title:"):
                line = line.replace("Book Title:", "").strip()
                self.title = line  # Update title immediately

            lines.append(line)

        return '\n'.join(lines).strip(), consensus

    def _force_consensus(self):
        """Force consensus with the last proposed title"""
        for msg in reversed(self.messages):
            if isinstance(msg, dict):
                content = msg.get("content", "") or ""
                if "Book Title:" in content:
                    self.title = content.split("Book Title:")[1].strip()
                    irc_logger.info("Forced consensus on the last proposed Book Title.")
                    return
        self.title = None
        irc_logger.warning("No valid Book Title found to force consensus.")

    def generate(self):
        """Generate a title through agent collaboration"""
        irc_logger.system_message(f"Enter a book topic: {self.topic}")

        initial_message = {
            "role": "user",
            "content": f"Let's collaborate on a title for a book about: {self.topic}. Please propose an initial title idea."
        }

        self.messages = [initial_message]
        attempt_count = 0
        max_attempts = TITLE_GENERATION.get("max_attempts", 10)
        max_consecutive_failures = 3
        consecutive_failures = 0
        current_agent = self.zero_agent

        try:
            while attempt_count < max_attempts and consecutive_failures < max_consecutive_failures:
                attempt_count += 1

                response = self.agents.client.run(
                    agent=current_agent,
                    messages=self.messages,
                    context_variables={"topic": self.topic},
                    max_turns=1,
                    debug=TITLE_GENERATION.get("debug", False)
                )

                if response is None or response.messages is None or not response.messages:
                    irc_logger.error("Received an invalid response from the agent.")
                    consecutive_failures += 1
                    continue

                last_message = response.messages[-1]
                content = last_message.get('content', '') or ''
                formatted_content, consensus = self.format_message(content)

                if not formatted_content:
                    irc_logger.error("Formatted content is empty.")
                    consecutive_failures += 1
                    continue

                irc_logger.agent_message(current_agent.name, formatted_content)
                self.messages.extend(response.messages)
                consecutive_failures = 0  # Reset on successful response

                if 'Consensus: True' in content and self.title:
                    irc_logger.success(f"Consensus reached on the book title: {self.title}")
                    break

                # Switch to the other agent
                current_agent = self.gustave_agent if current_agent.name == "Zero" else self.zero_agent
            else:
                irc_logger.warning("Max attempts or consecutive failures reached. Forcing consensus.")
                self._force_consensus()

        except Exception as e:
            irc_logger.error(f"Error during title generation: {str(e)}")
            traceback_str = traceback.format_exc()
            irc_logger.error(f"Traceback: {traceback_str}")
            return None

        if self.title:
            irc_logger.system_message(f"Final book title generated: {self.title}")
        else:
            irc_logger.error("Failed to generate a book title.")

        return self.title
