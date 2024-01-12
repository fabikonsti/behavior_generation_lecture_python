import torch
import torch.nn as nn
from torch.distributions.categorical import Categorical


def mlp(sizes, activation=nn.ReLU, output_activation=nn.Identity):
    """Returns a multi-layer perceptron"""
    mlp = nn.Sequential()
    for i in range(len(sizes) - 1):
        mlp.append(nn.Linear(sizes[i], sizes[i + 1]))
        if i < len(sizes) - 2:
            mlp.append(activation())
        else:
            mlp.append(output_activation())
    return mlp


class CategorialPolicy:
    def __init__(self, sizes: list[int], actions: list):
        assert sizes[-1] == len(actions)
        torch.manual_seed(1337)
        self.net = mlp(sizes=sizes)
        self.actions = actions
        self._actions_tensor = torch.as_tensor(actions, dtype=torch.float32).view(
            len(actions), -1
        )

    # make function to compute action distribution
    def _get_distribution(self, state: torch.Tensor):
        """Calls the model and returns a categorial distribution over the actions."""
        logits = self.net(state)
        return Categorical(logits=logits)

    def get_action(self, state: torch.Tensor, deterministic: bool = False):
        """Returns an action sample for the given state"""
        policy = self._get_distribution(state)
        if deterministic:
            return self.actions[policy.mode.item()]
        return self.actions[policy.sample().item()]

    def get_log_prob(self, states: torch.Tensor, actions: torch.Tensor):
        """Returns the log-probability for taking the action, when being the given state"""
        return self._get_distribution(states).log_prob(
            self._get_action_id_from_action(actions)
        )

    def _get_action_id_from_action(self, actions: torch.Tensor):
        """Returns the indices of the passed actions in self.actions"""
        reshaped_actions = actions.unsqueeze(1).expand(
            -1, self._actions_tensor.size(0), -1
        )
        reshaped_actions_tensor = self._actions_tensor.unsqueeze(0).expand(
            actions.size(0), -1, -1
        )
        return torch.where(
            torch.all(reshaped_actions == reshaped_actions_tensor, dim=-1)
        )[1]
