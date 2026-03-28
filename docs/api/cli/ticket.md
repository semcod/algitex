# `cli.ticket`

Ticket subcommands for algitex CLI.

## Functions

### `ticket_add`

```python
def ticket_add(title: str=typer.Argument(...), priority: str=typer.Option('normal', '--priority', '-p'), type: str=typer.Option('task', '--type', '-t'))
```

Add a new ticket.

### `ticket_list`

```python
def ticket_list(status: Optional[str]=typer.Option(None, '--status', '-s')) -> None
```

List tickets.

### `ticket_board`

```python
def ticket_board() -> None
```

Kanban board view.
