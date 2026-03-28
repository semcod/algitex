# Example 26: LiteLLM Proxy + Ollama - Native Algitex Integration

```bash
cd examples/26-litellm-proxy-ollama
```

**Własne proxy liteLLM** wbudowane w algitex - lepsze niż aider do pracy z Ollama.

## Dlaczego nie aider?

| Problem | Aider | LiteLLM Proxy |
|---------|-------|---------------|
| API key wymagana | ❌ Tak (nawet dla Ollama) | ✅ Nie |
| Warningi o modelu | ❌ Setki linii | ✅ Czysty output |
| Git wymagany | ❌ Tak | ✅ Nie |
| Konfiguracja | ❌ Skomplikowana | ✅ Prosta YAML |

## Architektura

```
┌─────────────────────────────────────────────────────────────┐
│                    Algitex CLI                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  analyze     │→ │ litellm      │→ │ ollama       │       │
│  │ (analiza)    │  │ proxy        │  │ (local LLM)  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         ↓                                                   │
│  ┌──────────────┐                                           │
│  │ TODO.md      │                                           │
│  └──────────────┘                                           │
│         ↓                                                   │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ auto_fix.py  │→ │ litellm      │→ Naprawa kodu           │
│  │ (przez API)  │  │ (chat)       │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## Szybki Start

```bash
# 1. Instalacja (WAŻNE: użyj [proxy] dla pełnej funkcjonalności)
pip install 'litellm[proxy]'

# 2. Konfiguracja proxy
make setup

# 3. Uruchom proxy
make proxy

# 4. W drugim terminalu - analiza i naprawa
algitex analyze
python auto_fix.py --limit 5
```

## Konfiguracja

### litellm_config.yaml

```yaml
model_list:
  - model_name: qwen-coder
    litellm_params:
      model: ollama/qwen3-coder:latest
      api_base: http://localhost:11434
      
  - model_name: llama3
    litellm_params:
      model: ollama/llama3:8b
      api_base: http://localhost:11434
      
  - model_name: codellama
    litellm_params:
      model: ollama/codellama:7b
      api_base: http://localhost:11434

general_settings:
  master_key: dummy-key  # Not needed for local models
  
routing_strategy: simple-shuffle
```

## Użycie

### 1. Uruchom proxy

```bash
litellm --config litellm_config.yaml --port 4000
```

### 2. Test proxy

```bash
curl http://localhost:4000/v1/models
```

### 3. Użyj przez OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:4000/v1",
    api_key="dummy-key"  # Not validated for local models
)

response = client.chat.completions.create(
    model="qwen-coder",
    messages=[{"role": "user", "content": "Fix this code: ..."}]
)
```

### 4. Auto-fix workflow

```bash
# Analiza
algitex analyze

# Naprawa przez proxy
python auto_fix.py
```

## Różnice vs Example 21 (aider)

| Cecha | Example 21 (aider) | Example 26 (litellm) |
|-------|-------------------|----------------------|
| Zależności | aider-chat, git | litellm |
| API key | Wymagana (dummy) | Opcjonalna |
| Output | Warningi | Czysty JSON |
| Kod naprawy | Aider TUI | Custom API client |
| Konfiguracja | CLI args | YAML file |

## Workflow naprawy kodu

### Metoda 1: Direct API

```python
# auto_fix.py używa proxy
def fix_code(file_path, issue_description):
    response = requests.post(
        "http://localhost:4000/v1/chat/completions",
        json={
            "model": "qwen-coder",
            "messages": [
                {"role": "system", "content": "You are a code reviewer. Fix the issue."},
                {"role": "user", "content": f"File: {file_path}\nIssue: {issue_description}"}
            ]
        }
    )
    return response.json()["choices"][0]["message"]["content"]
```

### Metoda 2: Algitex SDK

```python
from algitex import LocalLLM

llm = LocalLLM(proxy_url="http://localhost:4000")
fixed_code = llm.fix_issue(file_path, issue_description)
```

## Zalety liteLLM proxy

1. **Standardowy OpenAI API** - wszystkie narzędzia działają
2. **Routing** - failover między modelami
3. **Rate limiting** - ochrona Ollama
4. **Caching** - szybsze powtórzenia
5. **Monitoring** - widoczność użycia
6. **Bez API keys** - dla lokalnych modeli

## Komendy

```bash
make setup     # Stwórz config i sprawdź zależności
make proxy     # Uruchom litellm proxy
make test      # Test połączenia
make fix       # Uruchom auto_fix.py
make stop      # Zatrzymaj proxy
```

## Troubleshooting

**Błąd**: `litellm: command not found`
**Fix**: `pip install 'litellm[proxy]'`

**Błąd**: `No module named 'apscheduler'` lub `ImportError: Missing dependency`
**Fix**: `pip install 'litellm[proxy]'` (ważne: z nawiasami kwadratowymi!)

**Błąd**: `Connection refused`
**Fix**: Uruchom proxy: `make proxy`

**Błąd**: `Model not found`
**Fix**: Sprawdź `litellm_config.yaml` i czy model jest w Ollama

## Porównanie wszystkich podejść

| Podejście | Złożoność | Jakość | Prędkość | Offline |
|-----------|-----------|--------|----------|---------|
| Example 21 (aider) | Średnia | ⭐⭐⭐ | ⭐⭐ | ✅ |
| Example 26 (litellm) | Niska | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ |
| Continue.dev | Niska | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ |
| Claude Code | Średnia | ⭐⭐⭐⭐ | ⭐⭐ | ✅ |

## Next Steps

1. Uruchom `make setup`
2. Sprawdź `make test`
3. Uruchom `algitex analyze && make fix`

Więcej: https://docs.litellm.ai/docs/
