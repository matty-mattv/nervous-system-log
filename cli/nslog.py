"""
CLI client - talks to the API over HTTP, never touches the database
directly.

Java comparison: Typer is roughly analogous to a CLI framework like
picocli - @Command-annotated classes with @Option/@Parameters in
picocli become Typer's decorated functions with type-hinted
parameters. Same underlying idea (declare a command, declare its
arguments, framework handles parsing argv), different syntax.

Architecturally, this file plays the role of a REST client - like
using Spring's RestTemplate/WebClient from a separate process to call
your own API, rather than importing your service layer directly. This
is a deliberate choice: the CLI and API are two independent processes
that only talk over HTTP, exactly as any two separate microservices
would.
"""

import requests
import typer

app = typer.Typer()

API_BASE = "http://127.0.0.1:8000"


@app.command()
def check_in(
    entry_type: str = typer.Option(..., help="activation, completion, reparenting, or reflection"),
    origin: str = typer.Option(None, help="thought, sensation, both, or unclear"),
    sensation_location: str = typer.Option(None, help="chest, throat_neck_back, stomach, or other"),
    intensity: str = typer.Option(None, help="wave or storm"),
    trigger_category: str = typer.Option(None, help="social_uncertainty, attachment_relevant, work, unprompted_memory, or other"),
    resolution: str = typer.Option(None, help="discharged, interrupted, or ongoing"),
    note: str = typer.Option(None, help="Optional free-text note"),
):
    """
    Log a new entry via the API.

    Java comparison: this function is the picocli @Command method.
    Typer builds the --entry-type, --origin, etc. CLI flags directly
    from these parameter names and type hints - same idea as picocli
    building flags from @Option-annotated fields.
    """
    payload = {
        "entry_type": entry_type,
        "origin": origin,
        "sensation_location": sensation_location,
        "intensity": intensity,
        "trigger_category": trigger_category,
        "resolution": resolution,
        "note": note,
    }

    response = requests.post(f"{API_BASE}/entries", json=payload)

    if response.status_code != 200:
        typer.echo(f"Error: {response.json().get('detail', response.text)}")
        raise typer.Exit(code=1)

    entry = response.json()
    typer.echo(f"Logged entry #{entry['id']} at {entry['created_at']}")


@app.command()
def recent(limit: int = 10):
    """
    Show recent entries.
    """
    response = requests.get(f"{API_BASE}/entries", params={"limit": limit})

    if response.status_code != 200:
        typer.echo(f"Error: {response.text}")
        raise typer.Exit(code=1)

    entries = response.json()
    if not entries:
        typer.echo("No entries yet.")
        return

    for e in entries:
        typer.echo(
            f"#{e['id']} [{e['created_at']}] {e['entry_type']} "
            f"| {e['sensation_location'] or '-'} | {e['intensity'] or '-'} "
            f"| {e['trigger_category'] or '-'} -> {e['resolution'] or '-'}"
        )
        if e["note"]:
            typer.echo(f"    note: {e['note']}")


if __name__ == "__main__":
    app()