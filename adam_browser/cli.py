"""
Command Line Interface for Adam Browser

Provides a terminal-based interface for interacting with the Adam Browser
agent without the GUI. Supports interactive mode and batch command execution.
"""

import asyncio
import sys
from typing import Optional, List, Dict, Any
import click
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from loguru import logger

from .agent import AdamAgent, AgentState
from .config import config


class AdamCLI:
    """
    Command Line Interface for Adam Browser.
    
    Provides interactive terminal interface with rich formatting,
    real-time status updates, and command history.
    """
    
    def __init__(self):
        """Initialize the CLI."""
        self.console = Console()
        self.agent: Optional[AdamAgent] = None
        self.is_running = False
        self.command_history: List[str] = []
        self.current_status = "Initializing..."
        
        # CLI state
        self.show_debug = False
        self.auto_screenshot = False
        
    async def run(self) -> int:
        """
        Run the CLI interface.
        
        Returns:
            int: Exit code
        """
        try:
            # Show welcome banner
            self._show_banner()
            
            # Initialize agent
            if not await self._initialize_agent():
                self.console.print("[red]Failed to initialize agent[/red]")
                return 1
            
            # Start interactive loop
            await self._interactive_loop()
            
            return 0
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Interrupted by user[/yellow]")
            return 0
        except Exception as e:
            self.console.print(f"[red]CLI error: {e}[/red]")
            logger.error(f"CLI error: {e}")
            return 1
        finally:
            await self._cleanup()
    
    def _show_banner(self) -> None:
        """Show welcome banner."""
        banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                        ADAM BROWSER                          ║
║                 Autonomous AI Agent Browser                  ║
║                        Version {config.version}                        ║
╚══════════════════════════════════════════════════════════════╝

Welcome to Adam Browser CLI! 
Type 'help' for available commands or start giving natural language instructions.
        """
        
        self.console.print(Panel(banner, style="bold blue"))
    
    async def _initialize_agent(self) -> bool:
        """Initialize the Adam agent."""
        try:
            self.console.print("[yellow]Initializing Adam Agent...[/yellow]")
            
            self.agent = AdamAgent()
            
            # Set up callbacks
            self.agent.set_callbacks(
                on_state_change=self._on_state_change,
                on_command_complete=self._on_command_complete,
                on_error=self._on_error
            )
            
            # Start agent
            success = await self.agent.start()
            
            if success:
                self.console.print("[green]✓ Agent initialized successfully[/green]")
                self.is_running = True
                return True
            else:
                self.console.print("[red]✗ Failed to initialize agent[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]Initialization error: {e}[/red]")
            return False
    
    async def _interactive_loop(self) -> None:
        """Main interactive command loop."""
        self.console.print("\n[green]Agent ready! Enter commands or type 'quit' to exit.[/green]\n")
        
        while self.is_running:
            try:
                # Get user input
                command = await self._get_user_input()
                
                if not command:
                    continue
                
                # Handle special commands
                if await self._handle_special_command(command):
                    continue
                
                # Execute agent command
                await self._execute_command(command)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'quit' to exit[/yellow]")
            except EOFError:
                break
    
    async def _get_user_input(self) -> str:
        """Get user input with prompt."""
        try:
            # Show status
            status_text = f"[{self.agent.state.value}]" if self.agent else "[stopped]"
            
            prompt_text = f"Adam {status_text} > "
            command = Prompt.ask(prompt_text, console=self.console)
            
            return command.strip()
            
        except (KeyboardInterrupt, EOFError):
            raise
    
    async def _handle_special_command(self, command: str) -> bool:
        """
        Handle special CLI commands.
        
        Args:
            command: User command
            
        Returns:
            bool: True if command was handled, False otherwise
        """
        command_lower = command.lower()
        
        if command_lower in ['quit', 'exit', 'q']:
            await self._quit()
            return True
        
        elif command_lower in ['help', 'h', '?']:
            self._show_help()
            return True
        
        elif command_lower == 'status':
            await self._show_status()
            return True
        
        elif command_lower == 'history':
            self._show_history()
            return True
        
        elif command_lower == 'clear':
            self.console.clear()
            return True
        
        elif command_lower.startswith('debug '):
            self.show_debug = command_lower.endswith('on')
            self.console.print(f"[yellow]Debug mode: {'on' if self.show_debug else 'off'}[/yellow]")
            return True
        
        elif command_lower == 'screenshot':
            await self._take_screenshot()
            return True
        
        elif command_lower == 'metrics':
            await self._show_metrics()
            return True
        
        elif command_lower.startswith('config '):
            await self._handle_config_command(command[7:])
            return True
        
        return False
    
    async def _execute_command(self, command: str) -> None:
        """Execute an agent command."""
        if not self.agent:
            self.console.print("[red]Agent not initialized[/red]")
            return
        
        # Add to history
        self.command_history.append(command)
        
        # Show execution start
        self.console.print(f"[cyan]Executing:[/cyan] {command}")
        
        try:
            # Execute command
            result = await self.agent.process_command(command)
            
            # Show result
            if result.get('success', False):
                execution_time = result.get('execution_time', 0)
                self.console.print(f"[green]✓ Command completed in {execution_time:.2f}s[/green]")
                
                # Show additional result info if available
                if 'url' in result.get('execution_result', {}):
                    url = result['execution_result']['url']
                    self.console.print(f"[blue]Current URL:[/blue] {url}")
                
            else:
                error = result.get('error', 'Unknown error')
                self.console.print(f"[red]✗ Command failed: {error}[/red]")
            
            # Show debug info if enabled
            if self.show_debug:
                self._show_debug_info(result)
                
        except Exception as e:
            self.console.print(f"[red]Execution error: {e}[/red]")
    
    def _show_help(self) -> None:
        """Show help information."""
        help_text = """
[bold]Adam Browser CLI Commands[/bold]

[yellow]Natural Language Commands:[/yellow]
  • Go to google.com
  • Search for Python tutorials  
  • Click the login button
  • Type hello world
  • Scroll down 3 times
  • Book a flight from NYC to LA
  • Get directions to downtown
  • Take screenshot

[yellow]CLI Commands:[/yellow]
  • help, h, ?          - Show this help
  • status              - Show agent status
  • history             - Show command history
  • clear               - Clear screen
  • debug on/off        - Toggle debug mode
  • screenshot          - Take screenshot
  • metrics             - Show performance metrics
  • config <key> <val>  - Update configuration
  • quit, exit, q       - Exit application

[yellow]Examples:[/yellow]
  Adam [idle] > go to youtube.com
  Adam [idle] > search for AI tutorials
  Adam [idle] > click the first video
  Adam [idle] > screenshot
        """
        
        self.console.print(Panel(help_text, title="Help", style="blue"))
    
    async def _show_status(self) -> None:
        """Show agent status."""
        if not self.agent:
            self.console.print("[red]Agent not initialized[/red]")
            return
        
        status = self.agent.get_status()
        
        # Create status table
        table = Table(title="Agent Status", style="blue")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("State", status['state'])
        table.add_row("Running", str(status['is_running']))
        table.add_row("Queue Size", str(status['queue_size']))
        table.add_row("Commands Processed", str(status['metrics']['commands_processed']))
        table.add_row("Success Rate", f"{status['metrics']['success_rate']:.1f}%")
        table.add_row("Avg Response Time", f"{status['metrics']['average_response_time']:.2f}s")
        table.add_row("Uptime", f"{status['metrics']['uptime']:.1f}s")
        
        self.console.print(table)
    
    def _show_history(self) -> None:
        """Show command history."""
        if not self.command_history:
            self.console.print("[yellow]No command history[/yellow]")
            return
        
        table = Table(title="Command History", style="blue")
        table.add_column("#", style="cyan", width=4)
        table.add_column("Command", style="white")
        
        for i, command in enumerate(self.command_history[-10:], 1):  # Show last 10
            table.add_row(str(i), command)
        
        self.console.print(table)
    
    async def _take_screenshot(self) -> None:
        """Take a screenshot."""
        if not self.agent or not self.agent.browser_manager:
            self.console.print("[red]Browser not available[/red]")
            return
        
        try:
            screenshot_path = await self.agent.browser_manager.take_screenshot()
            if screenshot_path:
                self.console.print(f"[green]Screenshot saved: {screenshot_path}[/green]")
            else:
                self.console.print("[red]Failed to take screenshot[/red]")
        except Exception as e:
            self.console.print(f"[red]Screenshot error: {e}[/red]")
    
    async def _show_metrics(self) -> None:
        """Show performance metrics."""
        if not self.agent or not self.agent.database_manager:
            self.console.print("[red]Database not available[/red]")
            return
        
        try:
            metrics = await self.agent.database_manager.get_metrics_summary(hours=24)
            
            table = Table(title="Performance Metrics (24h)", style="blue")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="white")
            
            for key, value in metrics.items():
                if isinstance(value, float):
                    value = f"{value:.2f}"
                table.add_row(key.replace('_', ' ').title(), str(value))
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Metrics error: {e}[/red]")
    
    async def _handle_config_command(self, config_cmd: str) -> None:
        """Handle configuration commands."""
        parts = config_cmd.split()
        
        if len(parts) == 0:
            self.console.print("[yellow]Usage: config <key> [value][/yellow]")
            return
        
        key = parts[0]
        
        if len(parts) == 1:
            # Show config value
            value = config.get(key, "Not found")
            self.console.print(f"[cyan]{key}:[/cyan] {value}")
        else:
            # Set config value
            value = " ".join(parts[1:])
            # Note: This would need implementation in config module
            self.console.print(f"[yellow]Config update not implemented: {key} = {value}[/yellow]")
    
    def _show_debug_info(self, result: Dict[str, Any]) -> None:
        """Show debug information for a command result."""
        debug_table = Table(title="Debug Info", style="dim")
        debug_table.add_column("Property", style="cyan")
        debug_table.add_column("Value", style="white")
        
        debug_table.add_row("Command ID", result.get('command_id', 'N/A'))
        debug_table.add_row("Intent", str(result.get('intent', {})))
        debug_table.add_row("Execution Time", f"{result.get('execution_time', 0):.3f}s")
        
        self.console.print(debug_table)
    
    def _on_state_change(self, state: AgentState) -> None:
        """Handle agent state change."""
        if self.show_debug:
            self.console.print(f"[dim]State: {state.value}[/dim]")
    
    def _on_command_complete(self, result: Dict[str, Any]) -> None:
        """Handle command completion."""
        if self.show_debug:
            success = result.get('success', False)
            time_taken = result.get('execution_time', 0)
            status = "✓" if success else "✗"
            self.console.print(f"[dim]{status} Command completed in {time_taken:.2f}s[/dim]")
    
    def _on_error(self, error: Exception) -> None:
        """Handle agent error."""
        self.console.print(f"[red]Agent error: {error}[/red]")
    
    async def _quit(self) -> None:
        """Quit the CLI."""
        self.console.print("[yellow]Shutting down...[/yellow]")
        self.is_running = False
        
        if self.agent:
            await self.agent.stop()
    
    async def _cleanup(self) -> None:
        """Cleanup resources."""
        if self.agent:
            await self.agent.stop()
        
        self.console.print("[green]Goodbye![/green]")


# Click CLI for batch operations
@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--config', type=str, help='Configuration file path')
@click.pass_context
def cli(ctx, debug, config_file):
    """Adam Browser CLI - Autonomous AI Agent Browser"""
    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug
    ctx.obj['config'] = config_file


@cli.command()
@click.argument('command', nargs=-1, required=True)
@click.pass_context
async def execute(ctx, command):
    """Execute a single command and exit"""
    command_str = ' '.join(command)
    
    # Initialize CLI
    adam_cli = AdamCLI()
    
    try:
        # Initialize agent
        if not await adam_cli._initialize_agent():
            click.echo("Failed to initialize agent", err=True)
            return 1
        
        # Execute command
        await adam_cli._execute_command(command_str)
        
        return 0
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1
    finally:
        await adam_cli._cleanup()


@cli.command()
@click.pass_context
async def interactive(ctx):
    """Start interactive CLI mode"""
    adam_cli = AdamCLI()
    return await adam_cli.run()


if __name__ == "__main__":
    cli()
