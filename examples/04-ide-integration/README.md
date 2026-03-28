# Example 04: IDE Integration

Konfiguracja popularnych IDE/agentów do pracy z algitex + proxym.
Generuje fragmenty konfiguracji dla:

- Roo Code (VS Code)
- Cline (VS Code)
- Continue.dev
- Aider
- Cursor / Windsurf
- Claude Code

## Konfiguracja

Skopiuj i edytuj plik .env:

```bash
cp .env.example .env
# Edytuj .env z Twoimi wartościami
```

## Uruchomienie

```bash
./run.sh
```

## Co generuje

Dla każdego IDE pokazuje:
- URL endpoint proxym
- API key
- Mapowanie modeli (cheap/balanced/premium/free/local)

## Model aliases

| Alias      | Model             | Zastosowanie               |
|------------|-------------------|----------------------------|
| cheap      | Haiku 4.5         | debug, validation          |
| balanced   | Gemini Flash      | default coding             |
| premium    | Opus 4.6          | architecture, refactoring  |
| free       | Gemini 2.5        | planning, analysis         |
| local      | Qwen 3B           | offline, autocomplete      |

## Start proxym

```bash
# Opcja A: Docker
docker compose up -d

# Opcja B: CLI
proxym serve
```

Proxym będzie dostępny pod `http://localhost:4000`
