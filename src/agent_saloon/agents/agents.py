# src/agents/agents.py

try:
    from swarm import Agent, Swarm
except ImportError:
    Agent = None
    Swarm = None

class Agents:
    def __init__(self):
        if Swarm is None:
            raise ImportError(
                "The 'swarm' library is required. Install it via 'pip install swarm' or see README for details."
            )
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
