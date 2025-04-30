# Agent Saloon

Agent Saloon is an innovative project that orchestrates collaborative book writing using multi-agent systems. Through the power of OpenAI Swarm, specialized AI agents work together to generate comprehensive, well-structured books from concept to completion.

## Key Features

- 🤝 **Collaborative Writing** - Specialized agents Zero and Gustave work in tandem to generate titles, structure, and content
- 📑 **Smart Content Management** - Automated breakdown and organization of chapters and sections
- 🔄 **Iterative Refinement** - Consensus-driven process ensures high-quality content
- 📊 **Comprehensive Logging** - Detailed tracking of agent interactions and system processes

## Getting Started

### Prerequisites

- Python 3.10+
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/jmcdice/agent_saloon.git
cd agent_saloon
```

2. Set up virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install the package and its dependencies in editable mode:
```bash
pip install -e .
```

> **Note**: OpenAI Swarm is an experimental framework intended for educational purposes only.

## Usage

1. Activate the virtual environment (if not already active):
```bash
source .venv/bin/activate
```

2. Run the CLI command:
```bash
agent-saloon --chapters 5 "My Book Topic"
```
`agent-saloon` accepts a positional `topic` argument and an optional `--chapters` (or `-c`) flag to set the number of chapters.

3. Follow the interactive prompts to generate your book.

## Project Structure

```
agent_saloon/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
└── src/
    ├── agents/            # Agent configurations
    ├── models/            # Book generation logic
    ├── prompts/           # Agent prompt templates
    └── utils/             # Utility functions
```

## Example Output

After running the script, your generated book will be organized as follows:

```
books/your_book_title/
├── chapters/              # Individual chapters
├── sections/             # Detailed sections
├── final_book.md         # Complete compiled book
├── table_of_contents.txt
└── title.txt
```

## Technical Details

### Technologies

- **Python 3.10+**
- **OpenAI Swarm** - Experimental multi-agent orchestration framework
- **OpenAI GPT-4** - Core language model
- **Markdown** - Content formatting

### OpenAI Swarm Integration

Agent Saloon leverages OpenAI Swarm's experimental framework for:
- Agent orchestration and communication
- Handoff management between agents
- Lightweight, client-side execution
- Educational exploration of multi-agent systems

> **Important**: OpenAI Swarm is experimental and not intended for production use. It serves as an educational tool for exploring multi-agent patterns and practices.

## Contributing

While contributions to Agent Saloon are welcome for educational purposes, please note that the underlying OpenAI Swarm framework does not accept external contributions.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

