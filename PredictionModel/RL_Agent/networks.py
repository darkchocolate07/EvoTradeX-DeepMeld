import torch
import torch.nn as nn

class ActorCritic(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.actor = nn.Sequential(nn.Linear(state_dim, 64), nn.Tanh(), nn.Linear(64, 64), nn.Tanh(), nn.Linear(64, action_dim), nn.Softmax(dim=-1))
        self.critic = nn.Sequential(nn.Linear(state_dim, 64), nn.Tanh(), nn.Linear(64, 64), nn.Tanh(), nn.Linear(64, 1))
    def forward(self):
        raise NotImplementedError
    def act(self, state):
        dist = self.actor(state)
        dist = torch.distributions.Categorical(dist)
        action = dist.sample()
        logprob = dist.log_prob(action)
        return action.item(), logprob
    def evaluate(self, state, action):
        dist = self.actor(state)
        dist = torch.distributions.Categorical(dist)
        action_logprobs = dist.log_prob(action)
        dist_entropy = dist.entropy()
        value = self.critic(state)
        return action_logprobs, torch.squeeze(value), dist_entropy
