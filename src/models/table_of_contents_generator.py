# src/models/table_of_contents_generator.py

from src.agents import Agents
from src.prompts import TOC_PROMPT_ZERO, TOC_PROMPT_GUSTAVE
from src.config import TOC_GENERATION
from src.utils.irc_logger import irc_logger
import traceback

class TableOfContentsGenerator:
    def __init__(self, book_title):
        self.book_title = book_title
        self.agents = Agents()
        self.messages = []
        self.toc = None
        self._setup_agents()

    def _setup_agents(self):
        """Initialize the Zero and Gustave agents with ToC-specific prompts"""
        self.zero_agent = self.agents.get_zero(TOC_PROMPT_ZERO, self._handoff_to_gustave)
        self.gustave_agent = self.agents.get_gustave(TOC_PROMPT_GUSTAVE, self._handoff_to_zero)

    def _handoff_to_gustave(self):
        return self.gustave_agent

    def _handoff_to_zero(self):
        return self.zero_agent

    def format_message(self, content):
        """Formats the message content by removing system messages."""
        if not isinstance(content, str):
            content = str(content or "")
        lines = content.split('\n')
        filtered_lines = []
        for line in lines:
            if line.startswith("HANDOFF:") or line.startswith("functions."):
                continue
            filtered_lines.append(line)
        return '\n'.join(filtered_lines).strip()

    def _extract_toc(self, content):
        """Extract the agreed-upon table of contents from content"""
        if not content:
            irc_logger.error("No content to extract for Table of Contents.")
            return
        if "Table of Contents:" in content:
            self.toc = content.split("Table of Contents:")[1].strip()
        else:
            self.toc = content.strip()

    def _force_consensus(self):
        """Force consensus with the last proposed table of contents"""
        for msg in reversed(self.messages):
            if isinstance(msg, dict):
                content = msg.get("content", "") or ""
                if content.strip():
                    self._extract_toc(content)
                    irc_logger.info("Forced consensus on the last proposed Table of Contents.")
                    return
        self.toc = None
        irc_logger.warning("No valid Table of Contents found to force consensus.")

    def generate(self):
        """Generate a table of contents through agent collaboration"""
        initial_message = {
            "role": "user",
            "content": f"Let's collaborate on a table of contents for the book titled: {self.book_title}. Please propose an initial table of contents."
        }

        self.messages = [initial_message]
        attempt_count = 0
        max_attempts = TOC_GENERATION.get("max_attempts", 10)
        max_consecutive_failures = 3
        consecutive_failures = 0
        current_agent = self.zero_agent

        try:
            while attempt_count < max_attempts and consecutive_failures < max_consecutive_failures:
                attempt_count += 1

                response = self.agents.client.run(
                    agent=current_agent,
                    messages=self.messages,
                    context_variables={"book_title": self.book_title},
                    max_turns=1,
                    debug=TOC_GENERATION.get("debug", False)
                )

                if response is None or response.messages is None or not response.messages:
                    irc_logger.error("Received an invalid response from the agent.")
                    consecutive_failures += 1
                    continue

                last_message = response.messages[-1]
                content = last_message.get('content', '') or ''
                formatted_content = self.format_message(content)

                if not formatted_content:
                    irc_logger.error("Formatted content is empty.")
                    consecutive_failures += 1
                    continue

                irc_logger.agent_message(current_agent.name, formatted_content)
                self.messages.extend(response.messages)
                consecutive_failures = 0  # Reset on successful response

                if 'Consensus: True' in content:
                    self._extract_toc(content)
                    irc_logger.success("Consensus reached on the Table of Contents.")
                    break

                # Switch to the other agent
                current_agent = self._handoff_to_gustave() if current_agent.name == "Zero" else self._handoff_to_zero()
            else:
                irc_logger.warning("Max attempts or consecutive failures reached. Forcing consensus.")
                self._force_consensus()

        except Exception as e:
            irc_logger.error(f"Error during ToC generation: {str(e)}")
            traceback_str = traceback.format_exc()
            irc_logger.error(f"Traceback: {traceback_str}")
            return None

        if self.toc:
            irc_logger.system_message("Final Table of Contents generated successfully.")
        else:
            irc_logger.error("Failed to generate the table of contents.")

        return self.toc
