# `cli.docker`

Docker subcommands for algitex CLI.

## Functions

### `docker_list`

```python
def docker_list() -> None
```

List available Docker tools from docker-tools.yaml.

### `docker_spawn`

```python
def docker_spawn(tool_name: str=typer.Argument(...)) -> None
```

Start a Docker tool container.

### `docker_call`

```python
def docker_call(tool_name: str=typer.Argument(...), action: str=typer.Argument(...), input_json: Optional[str]=typer.Option(None, '--input', '-i', help='JSON input'))
```

Call an MCP tool on a running Docker container.

### `docker_teardown`

```python
def docker_teardown(tool_name: Optional[str]=typer.Argument(None))
```

Stop Docker tool containers.

### `docker_caps`

```python
def docker_caps(tool_name: str=typer.Argument(...))
```

List MCP capabilities of a Docker tool.
