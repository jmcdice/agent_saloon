# src/models/table_of_contents_generator.py

from src.agents import Agents
from src.prompts import TOC_PROMPT_ZERO, TOC_PROMPT_GUSTAVE
from src.config import TOC_GENERATION
from src.utils.irc_logger import irc_logger  # Ensure correct import path
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

    def _handoff_to_gustave(self, context_variables=None):
        return self.gustave_agent

    def _handoff_to_zero(self, context_variables=None):
        return self.zero_agent

    def format_message(self, content):
        """
        Formats the message content by removing system messages.
        System messages start with 'HANDOFF:' or contain 'functions.' calls.
        """
        lines = content.split('\n')
        filtered_lines = []
        for line in lines:
            if line.startswith("HANDOFF:") or line.startswith("functions."):
                continue
            filtered_lines.append(line)
        return '\n'.join(filtered_lines)

    def generate(self):
        """Generate a table of contents through agent collaboration"""
        initial_message = {
            "role": "user",
            "content": f"Let's collaborate on a table of contents for the book titled: {self.book_title}. Please propose an initial table of contents."
        }

        self.messages = [initial_message]
        attempt_count = 0

        try:
            response = self.agents.client.run(
                agent=self.zero_agent,
                messages=self.messages,
                context_variables={"book_title": self.book_title},
                debug=TOC_GENERATION["debug"]
            )

            if response is None or response.messages is None:
                irc_logger.error("Received an invalid response from the agent.")
                return None

            formatted_content = self.format_message(response.messages[-1].get('content', ''))
            irc_logger.agent_message(response.agent.name, formatted_content)
            self.messages.extend(response.messages)

            for _ in range(TOC_GENERATION["max_attempts"]):
                attempt_count += 1

                next_agent = self._handoff_to_gustave() if response.agent.name == "Zero" else self._handoff_to_zero()

                response = self.agents.client.run(
                    agent=next_agent,
                    messages=self.messages,
                    context_variables=response.context_variables,
                    debug=TOC_GENERATION["debug"]
                )

                if response is None or response.messages is None:
                    irc_logger.error("Received an invalid response from the agent.")
                    break

                formatted_content = self.format_message(response.messages[-1].get('content', ''))
                irc_logger.agent_message(response.agent.name, formatted_content)
                self.messages.extend(response.messages)

                # Check for consensus
                if any("Consensus: True" in msg.get("content", "") for msg in response.messages if msg):
                    self._extract_toc(response.messages)
                    irc_logger.success("Consensus reached on the Table of Contents.")
                    break

                if attempt_count >= TOC_GENERATION["max_attempts"]:
                    irc_logger.warning("Max attempts reached. Forcing consensus.")
                    self._force_consensus()
                    break

        except Exception as e:
            irc_logger.error(f"Error during ToC generation: {str(e)}")
            traceback_str = traceback.format_exc()
            irc_logger.error(f"Traceback: {traceback_str}")
            return None

        if self.toc and self.toc != "No table of contents reached":
            irc_logger.system_message("Final Table of Contents generated successfully.")
        else:
            irc_logger.error("Failed to generate the table of contents.")

        return self.toc

    def _extract_toc(self, messages):
        """Extract the agreed-upon table of contents from messages"""
        for msg in reversed(messages):
            if "Table of Contents:" in msg.get("content", ""):
                self.toc = msg["content"].split("Table of Contents:")[1].strip()
                return

    def _force_consensus(self):
        """Force consensus with the last proposed table of contents"""
        for msg in reversed(self.messages):
            if "Table of Contents:" in msg.get("content", ""):
                self.toc = msg["content"].split("Table of Contents:")[1].strip()
                irc_logger.info("Forced consensus on the last proposed Table of Contents.")
                return
        self.toc = "No table of contents reached"
        irc_logger.warning("No valid Table of Contents found to force consensus.")

    def get_toc(self):
        """Return the generated table of contents"""
        return self.toc

