# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

console = Console()


def check_env():
    missing = []
    required = ["GOOGLE_API_KEY", "YOUR_NAME"]
    for key in required:
        if not os.getenv(key):
            missing.append(key)
    if missing:
        console.print(f"[red]Missing in .env: {', '.join(missing)}[/red]")
        console.print("[yellow]Copy .env.example to .env and fill it[/yellow]")
        sys.exit(1)


def load_all_data(force_rebuild=False):
    from src.cv_loader import load_cv
    from src.github_fetcher import load_github
    from src.linkedin_loader import load_linkedin

    documents = []

    cv_path = os.getenv("CV_PDF_PATH", "data/cv.pdf")
    try:
        docs = load_cv(cv_path)
        documents.extend(docs)
    except FileNotFoundError as e:
        console.print(f"[yellow]{e}[/yellow]")

    github_user = os.getenv("GITHUB_USERNAME", "")
    github_token = os.getenv("GITHUB_TOKEN", "")
    if github_user:
        docs = load_github(github_user, github_token)
        documents.extend(docs)
    else:
        console.print("[yellow]Warning: No GITHUB_USERNAME in .env[/yellow]")

    linkedin_path = os.getenv("LINKEDIN_CSV_PATH", "data/linkedin_export.zip")
    docs = load_linkedin(linkedin_path)
    documents.extend(docs)

    return documents


def print_sources(source_docs):
    if not source_docs:
        return
    sources = list({doc.metadata.get("source", "Unknown") for doc in source_docs})
    console.print(f"[dim]Sources: {' | '.join(sources)}[/dim]")


def main():
    check_env()

    your_name = os.getenv("YOUR_NAME", "User")
    force_rebuild = "--rebuild" in sys.argv

    console.print(
        Panel.fit(
            f"[bold cyan]Personal AI Agent[/bold cyan]\n"
            f"[white]Answers questions about [bold]{your_name}[/bold][/white]\n"
            f"[dim]Type 'exit' or Ctrl+C to quit[/dim]\n"
            f"[dim]Type '--rebuild' to rebuild the vector store[/dim]",
            border_style="cyan",
        )
    )

    console.print("\n[bold]Loading your data...[/bold]")
    documents = load_all_data(force_rebuild)

    if not documents:
        console.print("[red]No data loaded! Check your files and try again.[/red]")
        sys.exit(1)

    total_chars = sum(len(d.page_content) for d in documents)
    console.print(f"\n[green]Loaded {len(documents)} source(s) ({total_chars:,} chars)[/green]")

    console.print("\n[bold]Building AI...[/bold]")
    from src.rag_chain import build_vectorstore, build_qa_chain

    vectorstore = build_vectorstore(documents, force_rebuild=force_rebuild)
    qa_chain = build_qa_chain(vectorstore, your_name)

    console.print(f"\n[bold green]Ready! Ask me about {your_name}[/bold green]\n")

    while True:
        try:
            question = Prompt.ask("[bold cyan]Your question[/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Goodbye![/yellow]")
            break

        if not question:
            continue

        if question.lower() in ("exit", "quit", "bye"):
            console.print("[yellow]Goodbye![/yellow]")
            break

        if question == "--rebuild":
            console.print("[yellow]Rebuilding vector store...[/yellow]")
            vectorstore = build_vectorstore(documents, force_rebuild=True)
            qa_chain = build_qa_chain(vectorstore, your_name)
            console.print("[green]Done![/green]\n")
            continue

        with console.status("[bold green]Thinking...[/bold green]", spinner="dots"):
            try:
                result = qa_chain.invoke({"question": question})
                answer = result.get("answer", "")
                source_docs = result.get("source_documents", [])
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]\n")
                continue

        console.print()
        console.print(
            Panel(
                Markdown(answer),
                title="[bold green]Answer[/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        )
        print_sources(source_docs)
        console.print()


if __name__ == "__main__":
    main()