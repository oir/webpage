from statistics import mean, pvariance
from math import sqrt
from hypothesis import given, strategies as st
import torch

def my_layernorm(x: list[float], epsilon: float = 1e-5) -> list[float]:
    """
    Applies Layer Normalization to the input list of floats.

    Args:
        x (list[float]): Input data to be normalized.
        epsilon (float): A small value to avoid division by zero.

    Returns:
        list[float]: The normalized output.
    """
    mu = mean(x)
    sigma2 = pvariance(x) if len(x) > 1 else 0.0

    normalized_x = [(xi - mu) / sqrt(sigma2 + epsilon) for xi in x]
    return normalized_x

def torch_layernorm(x: torch.Tensor, epsilon: float = 1e-5) -> torch.Tensor:
    """
    Applies Layer Normalization to the input tensor using PyTorch.

    Args:
        x (torch.Tensor): Input data to be normalized.
        epsilon (float): A small value to avoid division by zero.

    Returns:
        torch.Tensor: The normalized output.
    """
    return torch.nn.functional.layer_norm(x, x.size(), eps=epsilon)


# test my_layernorm against torch_layernorm using Hypothesis
@given(st.lists(st.floats(min_value=-1e6, max_value=1e6), min_size=1, max_size=100))
def test_layernorm_equivalence(input_data):
    custom_output = my_layernorm(input_data)
    torch_input = torch.tensor(input_data, dtype=torch.float32)
    torch_output = torch_layernorm(torch_input).tolist()

    # Assert that both outputs are approximately equal using relative tolerance
    for c_out, t_out in zip(custom_output, torch_output):
        assert abs(c_out - t_out) <= 1e-5 * max(abs(c_out), abs(t_out), 1.0)


if __name__ == "__main__":
    # Example usage
    input_data = [1.0, 2.0, 3.0, 4.0, 5.0]
    normalized_data = my_layernorm(input_data)
    print("Custom LayerNorm Output:", normalized_data)

    input_tensor = torch.tensor(input_data)
    normalized_tensor = torch_layernorm(input_tensor)
    print("PyTorch LayerNorm Output:", normalized_tensor.tolist())

    print(my_layernorm([-2, 0, 2]))