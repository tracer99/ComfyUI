import torch

import comfy.torch_directml_compat  # noqa: F401
import comfy_kitchen as ck


def test_current_kitchen_conv3d_runs_with_directml_torch():
    x = torch.ones(1, 1, 3, 3, 3)
    weight = torch.ones(1, 1, 2, 2, 2)
    result = ck.fp16_conv3d(x, weight, None, None, [1, 1, 1])
    assert result.shape == (1, 1, 2, 2, 2)
    torch.testing.assert_close(result, torch.full_like(result, 8))
