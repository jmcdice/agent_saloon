# src/utils/irc_logger.py

from rich.console import Console
from rich.theme import Theme

class IRCLogger:
    def __init__(self):
        # Set up Rich console with custom theme
        custom_theme = Theme({
            'zero': 'bold cyan',
            'gustave': 'bold blue',
            'system': 'dim white',
            'consensus_false': 'yellow',
            'consensus_true': 'bold green',
            'content': 'white',
            'final': 'bold magenta',
            'error': 'bold red',
            'info': 'blue',
            'warning': 'yellow',
            'success': 'bold green',
        })
        self.console = Console(theme=custom_theme)

    def agent_message(self, agent_name, content):
        """Print agent messages in IRC style"""
        try:
            # Format agent name with appropriate color
            agent_style = 'zero' if agent_name == "Zero" else 'gustave'
            # Remove line breaks and extra spaces from content
            cleaned_content = ' '.join(content.split())
            self.console.print(f"<[{agent_style}]{agent_name}[/{agent_style}]> {cleaned_content}")
        except Exception as e:
            self.console.print(f"[error]Error printing agent message: {str(e)}[/error]")

    def system_message(self, content):
        """Print system messages in IRC style"""
        try:
            self.console.print(f"[system]* {content}[/system]")
        except Exception as e:
            self.console.print(f"[error]Error printing system message: {str(e)}[/error]")

    def error(self, content):
        """Print error messages in IRC style"""
        try:
            self.console.print(f"[error]* Error: {content}[/error]")
        except Exception as e:
            self.console.print(f"[error]Critical error in error logging: {str(e)}[/error]")

    def info(self, content):
        """Print informational messages"""
        try:
            self.console.print(f"[info]* Info: {content}[/info]")
        except Exception as e:
            self.console.print(f"[error]Error printing info message: {str(e)}[/error]")

    def warning(self, content):
        """Print warning messages"""
        try:
            self.console.print(f"[warning]* Warning: {content}[/warning]")
        except Exception as e:
            self.console.print(f"[error]Error printing warning message: {str(e)}[/error]")

    def success(self, content):
        """Print success messages"""
        try:
            self.console.print(f"[success]* Success: {content}[/success]")
        except Exception as e:
            self.console.print(f"[error]Error printing success message: {str(e)}[/error]")

    def print_content(self, content):
        """Print large content blocks like Table of Contents"""
        try:
            self.console.print(content, style="content")
        except Exception as e:
            self.console.print(f"[error]Error printing content: {str(e)}[/error]")

# Create a singleton instance
irc_logger = IRCLogger()

