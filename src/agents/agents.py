# src/agents/agents.py

from swarm import Agent, Swarm

class Agents:
    def __init__(self):
        self.client = Swarm()

    def get_zero(self, instructions, handoff_func):
        """Get Zero agent with specific instructions"""
        return Agent(
            name="Zero",
            instructions=instructions,
            functions=[handoff_func]
        )

    def get_gustave(self, instructions, handoff_func):
        """Get Gustave agent with specific instructions"""
        return Agent(
            name="Gustave",
            instructions=instructions,
            functions=[handoff_func]
        )
