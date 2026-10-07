from __future__ import annotations

import comfy.memory_management as memory_management
import comfy.model_management as model_management


class OpaqueTensor:
    def __init__(self, nbytes: int = 64):
        self.nbytes = nbytes

    def untyped_storage(self):
        raise NotImplementedError("Cannot access storage of OpaqueTensorImpl")


def test_get_untyped_storage_returns_none_for_opaque_tensor():
    tensor = OpaqueTensor()

    assert memory_management.get_untyped_storage(tensor) is None


def test_read_tensor_file_slice_into_returns_false_for_opaque_tensor():
    tensor = OpaqueTensor()

    assert memory_management.read_tensor_file_slice_into(tensor, object()) is False


def test_cast_to_gathered_copies_opaque_tensor(monkeypatch):
    tensor = OpaqueTensor()
    copied = []

    class Destination:
        def copy_(self, source, non_blocking=False):
            copied.append(source)

    monkeypatch.setattr(memory_management, "interpret_gathered_like", lambda *args: [Destination()])
    model_management.cast_to_gathered([tensor], object())

    assert copied == [tensor]
