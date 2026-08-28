from algitex.tools.autofix import openrouter_backend


def test_autofix_uses_central_subllm(monkeypatch):
    captured = {}

    def fake_complete(application, function, messages, **kwargs):
        captured.update(application=application, function=function, messages=messages, kwargs=kwargs)
        return type("Response", (), {"content": "fixed"})()

    monkeypatch.setattr(openrouter_backend, "subllm_complete", fake_complete)
    backend = openrouter_backend.OpenRouterBackend(api_key="test-key")

    assert backend._call_api("repair this") == "fixed"
    assert captured["application"] == "semcod-algitex"
    assert captured["function"] == "autofix"
    assert captured["kwargs"]["credentials"] == {"OPENROUTER_API_KEY": "test-key"}
