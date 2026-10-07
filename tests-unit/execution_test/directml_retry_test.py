from types import SimpleNamespace

import pytest

import execution


@pytest.mark.asyncio
async def test_directml_oom_retries_once_with_clean_caches(monkeypatch):
    executor = object.__new__(execution.PromptExecutor)
    calls = []
    error = RuntimeError("Could not allocate tensor: not enough GPU video memory")

    async def execute_once(*args):
        calls.append(args)
        executor.cpu_retry_error = error if len(calls) == 1 else None

    def reset():
        calls.append("reset")
        executor.cpu_retry_error = None

    monkeypatch.setattr(executor, "_execute_async_once", execute_once)
    monkeypatch.setattr(executor, "reset", reset)
    monkeypatch.setattr(execution.comfy.model_management, "unload_all_models", lambda: None)
    monkeypatch.setattr(execution.comfy.model_management, "cleanup_models_gc", lambda: None)
    switched = []
    monkeypatch.setattr(execution.comfy.model_management, "switch_to_cpu_mode", switched.append)

    await executor.execute_async({}, "test-prompt", {}, [])

    assert len(calls) == 3
    assert calls[1] == "reset"
    assert switched == [error]


def test_other_execution_errors_are_reported(monkeypatch):
    server = SimpleNamespace(client_id=None)
    executor = object.__new__(execution.PromptExecutor)
    executor.server = server
    executor.cpu_retry_error = None
    executor.status_messages = []
    monkeypatch.setattr(execution.comfy.model_management, "should_retry_on_cpu_after_oom", lambda error: False)
    error = {
        "node_id": "1", "exception_message": "bad input", "exception_type": "ValueError",
        "traceback": [], "current_inputs": {},
    }
    executor.handle_execution_error("test", {"1": {"class_type": "Test"}}, [], [], error, ValueError("bad input"))
    assert executor.status_messages[0][0] == "execution_error"
