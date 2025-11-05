import requests
import typer
from typing import NamedTuple, Union, Any
from rich.console import Console

console = Console(highlight=False)
app = typer.Typer(
    add_completion=False,
    help="A simple CLI tool to change your Discord status.",
    no_args_is_help=True
)
commands = typer.Typer()
app.add_typer(commands, name="")


class UserInfo(NamedTuple):
    username: Union[str, None]
    is_valid_token: bool


def get_user_info(token: str) -> UserInfo:
    response = requests.get("https://discord.com/api/v10/users/@me", headers={'authorization': token})

    if response.ok:
        user_info: dict[str, Any] = response.json()
        return UserInfo(username=user_info["username"], is_valid_token=True)
    else:
        return UserInfo(username=None, is_valid_token=False)


def change_status(token: str, status: str) -> int:
    current_status: dict[str, Any] = requests.get(
        "https://discord.com/api/v8/users/@me/settings",
        headers={"authorization": token}
    ).json()

    custom_status: dict[str, Any] = current_status.get("custom_status") or {}
    custom_status["text"] = status

    response = requests.patch(
        "https://discord.com/api/v8/users/@me/settings",
        headers={"authorization": token},
        json={
            "custom_status": custom_status,
            "activities": current_status.get("activities") or []
        }
    )
    return response.status_code


@commands.command(
    name="change-status",
    help="Change your Discord status."
)
def change_status_command(
    token: str = typer.Option(..., help="Your Discord token"),
    status: str = typer.Option(..., help="The string to set as your Discord status")
):

    if (length := len(status)) > 128:
        amount_over = length - 128
        console.print(
            "[bold red]Error:[/bold red] "
            f"Your status is [bold yellow]{length}[/bold yellow] characters long, which is "
            f"[bold yellow]{amount_over}[/bold yellow] {'characters' if amount_over != 1 else 'character'} over "
            "the limit. Please shorten it to [bold yellow]128[/bold yellow] characters or less."
        )
        return

    user_info = get_user_info(token)

    if not user_info.is_valid_token:
        console.print("Invalid token.")
        return

    console.print(f"Status changed for [cyan]{user_info.username}[/cyan]: [yellow]'{status}'[/yellow]")
    change_status(token, status)


if __name__ == "__main__":
    app()
