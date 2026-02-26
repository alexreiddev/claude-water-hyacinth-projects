#!/usr/bin/env python3
"""
Personal Networking Directory
------------------------------
Log people you meet, then let Claude surface entrepreneurial
opportunities, collaborations, and follow-up actions.

Usage:
  python app.py add          # Add a new contact
  python app.py list         # List all contacts
  python app.py view <id>    # View a contact + their past analyses
  python app.py analyze <id> # Run Claude analysis on a contact
  python app.py network      # Analyze your whole network
  python app.py edit <id>    # Edit an existing contact
  python app.py delete <id>  # Delete a contact
  python app.py setup        # First-time setup (your profile)
"""

import click
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich import box
from dotenv import load_dotenv, set_key
from pathlib import Path
import db
import claude_client

load_dotenv()
console = Console()
ENV_PATH = Path(".env")


# ── helpers ──────────────────────────────────────────────────────────────────

def prompt_list(label: str, hint: str = "") -> list[str]:
    """Prompt for a comma-separated list, return as list of strings."""
    raw = Prompt.ask(f"[bold]{label}[/bold] [dim]{hint}[/dim]", default="")
    return [x.strip() for x in raw.split(",") if x.strip()]


def print_contact_table(contacts: list[dict]):
    table = Table(box=box.ROUNDED, show_lines=False)
    table.add_column("ID", style="dim", width=4)
    table.add_column("Name", style="bold white")
    table.add_column("Met", style="cyan", width=12)
    table.add_column("Profession", style="green")
    table.add_column("Industry", style="yellow")
    table.add_column("Skills", style="dim")

    for c in contacts:
        skills_preview = ", ".join(c.get("skills", [])[:3])
        if len(c.get("skills", [])) > 3:
            skills_preview += "…"
        table.add_row(
            str(c["id"]),
            c["name"],
            c.get("date_met", ""),
            c.get("profession", ""),
            c.get("industry", ""),
            skills_preview,
        )
    console.print(table)


def print_contact_detail(contact: dict):
    def fmt_list(lst):
        return ", ".join(lst) if lst else "—"

    lines = [
        f"**Name:** {contact['name']}",
        f"**Date met:** {contact.get('date_met', '—')}",
        f"**Where met:** {contact.get('where_met', '—')}",
        f"**Profession:** {contact.get('profession', '—')}",
        f"**Industry:** {contact.get('industry', '—')}",
        f"**Skills:** {fmt_list(contact.get('skills', []))}",
        f"**Interests:** {fmt_list(contact.get('interests', []))}",
        f"**Resources/assets:** {fmt_list(contact.get('resources', []))}",
        f"**Problems mentioned:** {fmt_list(contact.get('problems', []))}",
        f"**Notes:** {contact.get('notes', '—')}",
    ]
    console.print(Panel(
        Markdown("\n".join(lines)),
        title=f"[bold cyan]Contact #{contact['id']}[/bold cyan]",
        border_style="cyan",
    ))


# ── CLI commands ──────────────────────────────────────────────────────────────

@click.group()
def cli():
    """Personal networking directory powered by Claude."""
    db.init_db()


@cli.command()
def setup():
    """Set up your own profile so Claude has context about you."""
    console.print(Panel(
        "[bold]First-time setup[/bold]\n"
        "Tell Claude about yourself so it can give better entrepreneurial insights.",
        border_style="green",
    ))

    if not ENV_PATH.exists():
        ENV_PATH.write_text("")

    name = Prompt.ask("[bold]Your name[/bold]")
    skills = Prompt.ask("[bold]Your skills[/bold] [dim](comma-separated)[/dim]", default="")
    industry = Prompt.ask("[bold]Your industry / space[/bold]", default="")
    projects = Prompt.ask("[bold]Current projects or goals[/bold]", default="")

    set_key(ENV_PATH, "MY_NAME", name)
    set_key(ENV_PATH, "MY_SKILLS", skills)
    set_key(ENV_PATH, "MY_INDUSTRY", industry)
    set_key(ENV_PATH, "MY_CURRENT_PROJECTS", projects)

    api_key = Prompt.ask(
        "[bold]Anthropic API key[/bold] [dim](leave blank to skip)[/dim]",
        default="", password=True,
    )
    if api_key:
        set_key(ENV_PATH, "ANTHROPIC_API_KEY", api_key)

    console.print("[green]Profile saved to .env[/green]")


@cli.command("add")
def add_contact():
    """Add a new contact you met today."""
    console.print(Panel(
        "[bold]Add a new contact[/bold]\n"
        "Fill in what you know — leave anything blank if you don't have it yet.",
        border_style="blue",
    ))

    name = Prompt.ask("[bold]Name[/bold]")
    if not name.strip():
        console.print("[red]Name is required.[/red]")
        return

    date_met = Prompt.ask(
        "[bold]Date met[/bold]",
        default=datetime.now().strftime("%Y-%m-%d"),
    )
    where_met   = Prompt.ask("[bold]Where/how did you meet?[/bold]", default="")
    profession  = Prompt.ask("[bold]Profession / job title[/bold]", default="")
    industry    = Prompt.ask("[bold]Industry / domain[/bold]", default="")
    skills      = prompt_list("Skills / expertise", "(e.g. Python, fundraising, design)")
    interests   = prompt_list("Interests / passions", "(e.g. climate tech, travel, music)")
    resources   = prompt_list("Resources / assets", "(e.g. VC network, manufacturing contacts, $500k ARR biz)")
    problems    = prompt_list("Problems they mentioned", "(pain points, frustrations, things they want solved)")
    notes       = Prompt.ask("[bold]Free-form notes[/bold]", default="")

    contact_id = db.add_contact({
        "name": name,
        "date_met": date_met,
        "where_met": where_met,
        "profession": profession,
        "industry": industry,
        "skills": skills,
        "interests": interests,
        "resources": resources,
        "problems": problems,
        "notes": notes,
    })

    console.print(f"[green]Saved as contact #{contact_id}[/green]")

    if Confirm.ask("Run Claude opportunity analysis now?", default=True):
        _run_analysis(contact_id)


@cli.command("list")
@click.argument("search", required=False, default="")
def list_contacts(search):
    """List all contacts (optionally filter with SEARCH)."""
    contacts = db.list_contacts(search)
    if not contacts:
        console.print("[dim]No contacts found.[/dim]")
        return
    console.print(f"\n[bold]{len(contacts)} contact(s)[/bold]\n")
    print_contact_table(contacts)


@cli.command("view")
@click.argument("contact_id", type=int)
def view_contact(contact_id):
    """View a contact and their past analyses."""
    contact = db.get_contact(contact_id)
    if not contact:
        console.print(f"[red]No contact with id {contact_id}[/red]")
        return

    print_contact_detail(contact)

    analyses = db.get_analyses(contact_id)
    if analyses:
        console.print(f"\n[bold]{len(analyses)} past analysis/analyses[/bold]")
        for i, a in enumerate(analyses, 1):
            console.print(Panel(
                Markdown(a["analysis"]),
                title=f"[yellow]Analysis {i} — {a['created_at'][:10]}[/yellow]",
                border_style="yellow",
            ))
    else:
        console.print("[dim]No analyses yet. Run: python app.py analyze {contact_id}[/dim]")


@cli.command("analyze")
@click.argument("contact_id", type=int)
@click.option("--context", "-c", default="", help="Extra context or goal for this analysis")
def analyze(contact_id, context):
    """Run Claude AI opportunity analysis on a contact."""
    _run_analysis(contact_id, extra_context=context)


def _run_analysis(contact_id: int, extra_context: str = ""):
    contact = db.get_contact(contact_id)
    if not contact:
        console.print(f"[red]No contact with id {contact_id}[/red]")
        return

    console.print(f"\n[cyan]Analyzing {contact['name']} with Claude…[/cyan]")

    try:
        result = claude_client.analyze_contact(contact, extra_context=extra_context)
    except RuntimeError as e:
        console.print(f"[red]Error: {e}[/red]")
        return

    db.save_analysis(contact_id, result, context=extra_context)

    console.print(Panel(
        Markdown(result),
        title=f"[bold yellow]Opportunity Map — {contact['name']}[/bold yellow]",
        border_style="yellow",
    ))


@cli.command("network")
@click.option("--goal", "-g", default="", help="Your current goal or focus area")
def network_analysis(goal):
    """Analyze your whole network for patterns and cross-connections."""
    contacts = db.list_contacts()
    if not contacts:
        console.print("[dim]No contacts yet. Add some with: python app.py add[/dim]")
        return

    console.print(f"\n[cyan]Analyzing your network of {len(contacts)} contacts…[/cyan]")

    try:
        result = claude_client.analyze_network(contacts, goal=goal)
    except RuntimeError as e:
        console.print(f"[red]Error: {e}[/red]")
        return

    console.print(Panel(
        Markdown(result),
        title="[bold magenta]Network Intelligence Report[/bold magenta]",
        border_style="magenta",
    ))


@cli.command("edit")
@click.argument("contact_id", type=int)
def edit_contact(contact_id):
    """Edit an existing contact's data."""
    contact = db.get_contact(contact_id)
    if not contact:
        console.print(f"[red]No contact with id {contact_id}[/red]")
        return

    print_contact_detail(contact)
    console.print("[dim]Press Enter to keep existing values.[/dim]\n")

    def ask(label, key, is_list=False):
        current = contact.get(key, "")
        if is_list:
            current_str = ", ".join(current) if current else ""
            new_val = Prompt.ask(f"[bold]{label}[/bold]", default=current_str)
            return [x.strip() for x in new_val.split(",") if x.strip()]
        return Prompt.ask(f"[bold]{label}[/bold]", default=current or "")

    updates = {
        "name":       ask("Name", "name"),
        "date_met":   ask("Date met", "date_met"),
        "where_met":  ask("Where met", "where_met"),
        "profession": ask("Profession", "profession"),
        "industry":   ask("Industry", "industry"),
        "skills":     ask("Skills", "skills", is_list=True),
        "interests":  ask("Interests", "interests", is_list=True),
        "resources":  ask("Resources", "resources", is_list=True),
        "problems":   ask("Problems mentioned", "problems", is_list=True),
        "notes":      ask("Notes", "notes"),
    }

    db.update_contact(contact_id, updates)
    console.print(f"[green]Contact #{contact_id} updated.[/green]")


@cli.command("delete")
@click.argument("contact_id", type=int)
def delete_contact(contact_id):
    """Delete a contact and all their analyses."""
    contact = db.get_contact(contact_id)
    if not contact:
        console.print(f"[red]No contact with id {contact_id}[/red]")
        return

    if Confirm.ask(f"Delete [bold]{contact['name']}[/bold] and all their analyses?", default=False):
        db.delete_contact(contact_id)
        console.print(f"[green]Deleted contact #{contact_id}.[/green]")
    else:
        console.print("[dim]Cancelled.[/dim]")


if __name__ == "__main__":
    cli()
