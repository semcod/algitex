# `tools.tickets`

Tickets wrapper — manage planfile tickets without the ceremony.

Usage:
    from algitex.tools.tickets import Tickets

    t = Tickets("./my-project")
    t.add("Fix god module in cli.py", priority="high")
    t.from_analysis(report)    # auto-create tickets from analysis
    t.list()                   # show current sprint
    t.sync()                   # push to GitHub/Jira


## Classes

### `Ticket`

A single work item.

**Methods:**

#### `to_dict`

```python
def to_dict(self) -> dict
```

### `Tickets`

Manage project tickets via planfile or local YAML.

**Methods:**

#### `__init__`

```python
def __init__(self, project_path: str='.', config: Optional[TicketConfig]=None)
```

#### `add`

```python
def add(self, title: str) -> Ticket
```

Create a new ticket.

#### `from_analysis`

```python
def from_analysis(self, report) -> list[Ticket]
```

Auto-generate tickets from a HealthReport.

#### `list`

```python
def list(self, status: Optional[str]=None) -> list[Ticket]
```

List tickets, optionally filtered by status.

#### `update`

```python
def update(self, ticket_id: str, **kwargs) -> Optional[Ticket]
```

Update a ticket by ID.

#### `sync`

```python
def sync(self) -> dict
```

Sync tickets to external backend (GitHub, Jira, etc.).

#### `board`

```python
def board(self) -> dict[str, list[Ticket]]
```

Kanban-style board view.
