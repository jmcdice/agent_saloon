# src/utils/irc_logger.py

try:
    from rich.console import Console
    from rich.theme import Theme
except ImportError:
    Console = None  # fallback if rich is not installed
    Theme = None

class IRCLogger:
    def __init__(self):
        # Set up Rich console with custom theme if available
        if Console and Theme:
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
        else:
            self.console = None

    def agent_message(self, agent_name, content):
        """Print agent messages in IRC style"""
        try:
            cleaned_content = ' '.join(content.split())
            if self.console:
                agent_style = 'zero' if agent_name == "Zero" else 'gustave'
                self.console.print(f"<[{agent_style}]{agent_name}[/{agent_style}]> {cleaned_content}")
            else:
                print(f"[{agent_name}] {cleaned_content}")
        except Exception as e:
            if self.console:
                self.console.print(f"[error]Error printing agent message: {str(e)}[/error]")
            else:
                print(f"Error printing agent message: {str(e)}")

    def system_message(self, content):
        """Print system messages in IRC style"""
        try:
            if self.console:
                self.console.print(f"[system]* {content}[/system]")
            else:
                print(f"* {content}")
        except Exception as e:
            if self.console:
                self.console.print(f"[error]Error printing system message: {str(e)}[/error]")
            else:
                print(f"Error printing system message: {str(e)}")

    def error(self, content):
        """Print error messages in IRC style"""
        try:
            if self.console:
                self.console.print(f"[error]* Error: {content}[/error]")
            else:
                print(f"Error: {content}")
        except Exception as e:
            if self.console:
                self.console.print(f"[error]Critical error in error logging: {str(e)}[/error]")
            else:
                print(f"Critical error in error logging: {str(e)}")

    def info(self, content):
        """Print informational messages"""
        try:
            if self.console:
                self.console.print(f"[info]* Info: {content}[/info]")
            else:
                print(f"Info: {content}")
        except Exception as e:
            if self.console:
                self.console.print(f"[error]Error printing info message: {str(e)}[/error]")
            else:
                print(f"Error printing info message: {str(e)}")

    def warning(self, content):
        """Print warning messages"""
        try:
            if self.console:
                self.console.print(f"[warning]* Warning: {content}[/warning]")
            else:
                print(f"Warning: {content}")
        except Exception as e:
            if self.console:
                self.console.print(f"[error]Error printing warning message: {str(e)}[/error]")
            else:
                print(f"Error printing warning message: {str(e)}")

    def success(self, content):
        """Print success messages"""
        try:
            if self.console:
                self.console.print(f"[success]* Success: {content}[/success]")
            else:
                print(f"Success: {content}")
        except Exception as e:
            if self.console:
                self.console.print(f"[error]Error printing success message: {str(e)}[/error]")
            else:
                print(f"Error printing success message: {str(e)}")

    def print_content(self, content):
        """Print large content blocks like Table of Contents"""
        try:
            if self.console:
                self.console.print(content, style="content")
            else:
                print(content)
        except Exception as e:
            if self.console:
                self.console.print(f"[error]Error printing content: {str(e)}[/error]")
            else:
                print(f"Error printing content: {str(e)}")

# Create a singleton instance
irc_logger = IRCLogger()

