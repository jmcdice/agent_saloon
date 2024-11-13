# src/models/section_writer.py

from src.agents.agents import Agents
from src.prompts.section_prompts import SECTION_PROMPT_ZERO, SECTION_PROMPT_GUSTAVE
from src.utils.irc_logger import irc_logger
from src.config import SECTION_GENERATION  # Ensure you have this config
import traceback

class SectionWriter:
    def __init__(self, book_title, full_toc, section_number, section_title):
        self.book_title = book_title
        self.full_toc = full_toc
        self.section_number = section_number
        self.section_title = section_title
        self.agents = Agents()
        self.messages = []
        self.section_content = None
        self.title = None
        self._setup_agents()

    def _setup_agents(self):
        """Initialize the Zero and Gustave agents with section-specific prompts"""
        formatted_zero_prompt = SECTION_PROMPT_ZERO.format(
            book_title=self.book_title,
            full_toc=self.full_toc,
            section_number=self.section_number,
            section_title=self.section_title
        )
        formatted_gustave_prompt = SECTION_PROMPT_GUSTAVE.format(
            book_title=self.book_title,
            full_toc=self.full_toc,
            section_number=self.section_number,
            section_title=self.section_title
        )

        # Initialize agents with the instance handoff methods
        self.zero_agent = self.agents.get_zero(formatted_zero_prompt, self._handoff_to_gustave)
        self.gustave_agent = self.agents.get_gustave(formatted_gustave_prompt, self._handoff_to_zero)

    def _handoff_to_gustave(self):
        """Function to hand off control to Gustave."""
        return self.gustave_agent

    def _handoff_to_zero(self):
        """Function to hand off control back to Zero."""
        return self.zero_agent

    def _format_message(self, content):
        """
        Formats the message content by removing system messages and extracting consensus.
        """
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

            lines.append(line)

        return '\n'.join(lines).strip(), consensus

    def _extract_section_content(self, content):
        """Extract the section content from the agent's response"""
        # Implement extraction logic as needed
        # For example, you might parse the content to separate title and body
        self.section_content = content  # Placeholder implementation

    def _extract_title(self, content):
        """Extract the agreed-upon title from the agent's response content"""
        lines = content.split('\n')
        for line in lines:
            if "Book Title:" in line:
                self.title = line.split("Book Title:")[1].strip()
                return self.title
        return None

    def _force_consensus(self):
        """Force consensus with the last proposed title"""
        for msg in reversed(self.messages):
            if isinstance(msg, dict):  # Ensure msg is a dictionary
                content = msg.get("content", "")
                if "Book Title:" in content:
                    self.title = content.split("Book Title:")[1].strip()
                    irc_logger.info("Forced consensus on the last proposed Book Title.")
                    return
        self.title = "No title reached"
        irc_logger.warning("No valid Book Title found to force consensus.")

    def write(self):
        """Generate section content through agent collaboration"""
        initial_message = {
            'role': 'user',
            'content': f"Let's collaborate on writing the section {self.section_number}: {self.section_title}."
        }
        self.messages = [initial_message]
        attempt_count = 0
        max_attempts = SECTION_GENERATION.get("max_attempts", 10)
        current_agent = self.zero_agent

        try:
            while attempt_count < max_attempts:
                attempt_count += 1
                response = self.agents.client.run(
                    agent=current_agent,
                    messages=self.messages,
                    context_variables={
                        'book_title': self.book_title,
                        'full_toc': self.full_toc,
                        'section_number': self.section_number,
                        'section_title': self.section_title
                    },
                    max_turns=1,
                    debug=SECTION_GENERATION.get("debug", False)
                )

                if response is None or response.messages is None:
                    irc_logger.error('Received an invalid response from the agent.')
                    break

                last_message = response.messages[-1]
                formatted_content, consensus = self._format_message(last_message.get('content', ''))
                
                # Ensure formatted_content is a string
                if not isinstance(formatted_content, str):
                    irc_logger.error("Formatted content is not a string.")
                    break

                irc_logger.agent_message(current_agent.name, formatted_content)
                self.messages.extend(response.messages)

                if 'Consensus: True' in last_message.get('content', ''):
                    self._extract_section_content(last_message.get('content', ''))
                    irc_logger.success(f'Consensus reached on Section {self.section_number}: {self.section_title}.')
                    break

                # Switch to the other agent
                current_agent = self._handoff_to_gustave() if current_agent.name == 'Zero' else self._handoff_to_zero()
            else:
                irc_logger.warning('Max attempts reached. Forcing consensus.')
                self._force_consensus()

        except Exception as e:
            irc_logger.error(f'Error during section writing: {str(e)}')
            traceback_str = traceback.format_exc()
            irc_logger.error(f'Traceback: {traceback_str}')
            return None

        if self.section_content:
            irc_logger.system_message(f'Section {self.section_number}: {self.section_title} generated successfully.')
        else:
            irc_logger.error(f'Failed to generate Section {self.section_number}: {self.section_title}.')

        return self.section_content

