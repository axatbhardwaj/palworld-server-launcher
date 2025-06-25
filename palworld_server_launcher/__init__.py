"""
A simple tool to install and manage a Palworld dedicated server on Linux.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional

import rich
import typer
from rich.console import Console

app = typer.Typer()
console = Console()
STEAM_DIR = Path.home() / ".steam/steam"


def _get_template(name: str) -> str:
    """Reads a template file from the script's directory."""
    template_path = Path(__file__).parent / "templates" / name
    try:
        return template_path.read_text()
    except FileNotFoundError:
        rich.print(
            f"Error: Template file not found at {template_path}", file=sys.stderr
        )
        sys.exit(1)


def _run_command(command: str, check: bool = True) -> None:
    """Runs a command and prints its output in real-time."""
    console.print(f"Executing: [bold cyan]{command}[/bold cyan]")
    try:
        with subprocess.Popen(
            command,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ) as process:
            if process.stdout:
                for line in iter(process.stdout.readline, ""):
                    rich.print(line, end="")

            return_code = process.wait()

            if check and return_code != 0:
                raise subprocess.CalledProcessError(return_code, command)

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        rich.print(f"\nError executing command: {e}", file=sys.stderr)
        sys.exit(1)


def _repair_package_manager() -> None:
    """Tries to repair the apt/dpkg system."""
    console.print("Attempting to repair package manager...")
    _run_command("sudo pkill -f 'apt|dpkg'", check=False)
    _run_command("sudo rm /var/lib/apt/lists/lock", check=False)
    _run_command("sudo rm /var/cache/apt/archives/lock", check=False)
    _run_command("sudo rm /var/lib/dpkg/lock*", check=False)
    _run_command("sudo rm /var/cache/debconf/*.dat", check=False)
    _run_command("sudo dpkg --configure -a", check=False)
    _run_command("sudo apt-get -f install -y")
    _run_command("sudo apt-get autoremove -y", check=False)
    _run_command("sudo apt-get clean")
    _run_command("sudo apt update")


def _install_steamcmd() -> None:
    """Install steamcmd if not already installed."""
    _repair_package_manager()
    console.print("Checking for steamcmd...")
    try:
        subprocess.run(
            "command -v steamcmd", check=True, shell=True, capture_output=True
        )
        console.print("steamcmd is already installed.")
    except subprocess.CalledProcessError:
        console.print("steamcmd not found. Installing steamcmd...")
        _run_command("sudo apt install -y software-properties-common")
        _run_command("sudo add-apt-repository multiverse -y")
        _run_command("sudo dpkg --add-architecture i386")
        _run_command("sudo apt update")
        _run_command(
            "echo 'steam steam/question select \"I AGREE\"' | sudo debconf-set-selections"
        )
        _run_command(
            "echo 'steam steam/license note \"\"' | sudo debconf-set-selections"
        )
        _run_command("sudo apt install -y steamcmd")


def _install_palworld() -> None:
    """Install Palworld dedicated server using steamcmd."""
    console.print("Installing Palworld dedicated server...")
    _run_command("steamcmd +login anonymous +app_update 2394010 validate +quit")
    pal_server_script = STEAM_DIR / "steamapps/common/PalServer/PalServer.sh"
    if pal_server_script.exists():
        _run_command(f"chmod +x {pal_server_script}")


def _fix_steam_sdk() -> None:
    """Fix Steam SDK errors."""
    console.print("Fixing Steam SDK errors...")
    steam_sdk_path = Path.home() / ".steam/sdk64"
    steam_sdk_path.mkdir(parents=True, exist_ok=True)
    steam_client_so = (
        STEAM_DIR / "steamapps/common/Steamworks SDK Redist/linux64/steamclient.so"
    )
    if steam_client_so.exists():
        _run_command(f"cp {steam_client_so} {steam_sdk_path}/")
    else:
        rich.print(
            f"Warning: {steam_client_so} not found. This might cause issues.",
            file=sys.stderr,
        )


def _create_service_file(port: int, players: int) -> None:
    """Create a systemd service for the Pal Server."""
    console.print("Creating Pal Server service...")
    user = Path.home().name
    service_file = Path("/etc/systemd/system/palserver.service")
    template = _get_template("palserver.service.template")
    pal_server_dir = STEAM_DIR / "steamapps/common/PalServer"
    exec_start_path = pal_server_dir / "PalServer.sh"
    service_content = template.format(
        user=user,
        port=port,
        players=players,
        exec_start_path=exec_start_path,
        working_directory=pal_server_dir,
    )
    _run_command(f"echo '{service_content}' | sudo tee {service_file}")
    _run_command("sudo systemctl daemon-reload")


def _setup_polkit() -> None:
    """Allow user to control the service without sudo."""
    console.print("Setting up policy for non-sudo control...")
    user = Path.home().name
    policy_file = Path("/etc/polkit-1/rules.d/40-palserver.rules")
    _run_command(f"sudo mkdir -p {policy_file.parent}")
    template = _get_template("palserver.rules.template")
    policy_content = template.format(user=user)
    _run_command(f"echo '{policy_content}' | sudo tee {policy_file}")
    _run_command("sudo systemctl restart polkit.service")


@app.command()
def install(
    port: int = typer.Option(8211, help="Port to run the server on."),
    players: int = typer.Option(32, help="Maximum number of players."),
    start: bool = typer.Option(
        False, "--start", help="Start the server immediately after installation."
    ),
) -> None:
    """Install the Palworld dedicated server and create a systemd service."""
    if Path.home() == Path("/root"):
        rich.print("This script should not be run as root. Exiting.", file=sys.stderr)
        sys.exit(1)

    _install_steamcmd()
    _install_palworld()
    _fix_steam_sdk()
    _create_service_file(port, players)
    _setup_polkit()

    console.print("Installation complete!")

    if start:
        console.print("Starting the server...")
        _run_command("systemctl start palserver")
        console.print("Server started successfully!")
    else:
        console.print(
            "You can now start the server with: palworld-server-launcher start"
        )

    console.print(
        "To enable the server to start on boot, run: palworld-server-launcher enable"
    )


@app.command()
def start() -> None:
    """Start the Palworld server."""
    _run_command("systemctl start palserver")


@app.command()
def stop() -> None:
    """Stop the Palworld server."""
    _run_command("systemctl stop palserver")


@app.command()
def restart() -> None:
    """Restart the Palworld server."""
    _run_command("systemctl restart palserver")


@app.command()
def status() -> None:
    """Check the status of the Palworld server."""
    _run_command("systemctl status palserver", check=False)


@app.command()
def enable() -> None:
    """Enable the Palworld server to start on boot."""
    _run_command("systemctl enable palserver")


@app.command()
def disable() -> None:
    """Disable the Palworld server from starting on boot."""
    _run_command("systemctl disable palserver")


if __name__ == "__main__":
    app()
