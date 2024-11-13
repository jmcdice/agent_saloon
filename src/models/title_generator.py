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

    def _handoff_to_gustave(self, context_variables=None):
        return self.gustave_agent

    def _handoff_to_zero(self, context_variables=None):
        return self.zero_agent

    def format_message(self, content):
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

    def generate(self):
        """Generate a title through agent collaboration"""
        irc_logger.system_message(f"Enter a book topic: {self.topic}")

        initial_message = {
            "role": "user",
            "content": f"Let's collaborate on a title for a book about: {self.topic}. Please propose an initial title idea."
        }

        self.messages = [initial_message]
        attempt_count = 0

        try:
            current_agent = self.zero_agent
            max_attempts = TITLE_GENERATION["max_attempts"]
    
            while attempt_count < max_attempts:
                attempt_count += 1
    
                response = self.agents.client.run(
                    agent=current_agent,
                    messages=self.messages,
                    context_variables={"topic": self.topic},
                    max_turns=1,
                    debug=TITLE_GENERATION["debug"]
                )
    
                if response is None or response.messages is None:
                    irc_logger.error("Received an invalid response from the agent.")
                    break
    
                last_message = response.messages[-1]
                formatted_content, consensus = self.format_message(last_message.get('content', ''))
                irc_logger.agent_message(current_agent.name, formatted_content)
                self.messages.extend(response.messages)
    
                # Check for consensus
                if any("Consensus: True" in (msg.get("content", "") or "") for msg in response.messages if msg):
                    self.title = self._extract_title(last_message.get('content', ''))
                    irc_logger.success(f"Consensus reached on the book title: {self.title}")
                    break
    
                # Switch to the other agent
                current_agent = self.gustave_agent if current_agent.name == "Zero" else self.zero_agent
    
            else:
                irc_logger.warning("Max attempts reached. Forcing consensus.")
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
    

        try:
            response = self.agents.client.run(
                agent=self.zero_agent,
                messages=self.messages,
                context_variables={"book_topic": self.topic},
                debug=TITLE_GENERATION["debug"]
            )

            if response is None or response.messages is None:
                irc_logger.error("Received an invalid response from the agent.")
                return None

            formatted_content, consensus = self.format_message(response.messages[-1].get('content', ''))
            irc_logger.agent_message(response.agent.name, formatted_content)
            self.messages.extend(response.messages)

            for _ in range(TITLE_GENERATION["max_attempts"]):
                attempt_count += 1

                next_agent = self._handoff_to_gustave() if response.agent.name == "Zero" else self._handoff_to_zero()

                response = self.agents.client.run(
                    agent=next_agent,
                    messages=self.messages,
                    context_variables=response.context_variables,
                    debug=TITLE_GENERATION["debug"]
                )

                if response is None or response.messages is None:
                    irc_logger.error("Received an invalid response from the agent.")
                    break

                formatted_content, consensus = self.format_message(response.messages[-1].get('content', ''))
                irc_logger.agent_message(response.agent.name, formatted_content)
                self.messages.extend(response.messages)

                # Check for consensus
                if any("Consensus: True" in msg.get("content", "") for msg in response.messages if msg):
                    self._extract_title(response.messages)
                    irc_logger.success("Consensus reached on the Book Title.")
                    break

                if attempt_count >= TITLE_GENERATION["max_attempts"]:
                    irc_logger.warning("Max attempts reached. Forcing consensus.")
                    self._force_consensus()
                    break

            else:
                irc_logger.warning("Max attempts reached. Forcing consensus.")
                self._force_consensus()

        except Exception as e:
            irc_logger.error(f"Error during title generation: {str(e)}")
            traceback_str = traceback.format_exc()
            irc_logger.error(f"Traceback: {traceback_str}")
            return None

        if self.title and self.title != "No title reached":
            irc_logger.system_message(f"Final Book Title: {self.title}")
        else:
            irc_logger.error("Failed to generate a book title.")

        return self.title

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
            if "Book Title:" in msg.get("content", ""):
                self.title = msg["content"].split("Book Title:")[1].strip()
                irc_logger.info("Forced consensus on the last proposed Book Title.")
                return
        self.title = "No title reached"
        irc_logger.warning("No valid Book Title found to force consensus.")

    def get_title(self):
        """Return the generated title"""
        return self.title

