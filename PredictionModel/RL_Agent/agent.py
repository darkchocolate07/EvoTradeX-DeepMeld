import torch
import torch.nn as nn
import torch.optim as optim
from RL.networks import ActorCritic
from RL.memory import RolloutBuffer

class PPO:
    def __init__(self, state_dim, action_dim, lr, gamma, eps_clip, update_timestep, k_epochs):
        self.gamma = gamma
        self.eps_clip = eps_clip
        self.k_epochs = k_epochs
        self.update_timestep = update_timestep
        self.buffer = RolloutBuffer()
        self.policy = ActorCritic(state_dim, action_dim)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)
        self.policy_old = ActorCritic(state_dim, action_dim)
        self.policy_old.load_state_dict(self.policy.state_dict())
        self.MseLoss = nn.MSELoss()
        self.timestep = 0
    def select_action(self, state):
        state = torch.FloatTensor(state)
        action, logprob = self.policy_old.act(state)
        return action, logprob
    def update(self):
        rewards = []
        discounted_reward = 0
        for reward, is_terminal in zip(reversed(self.buffer.rewards), reversed(self.buffer.is_terminals)):
            if is_terminal:
                discounted_reward = 0
            discounted_reward = reward + (self.gamma * discounted_reward)
            rewards.insert(0, discounted_reward)
        rewards = torch.tensor(rewards, dtype=torch.float32)
        rewards = (rewards - rewards.mean())/(rewards.std() + 1e-7)
        old_states = torch.FloatTensor(self.buffer.states)
        old_actions = torch.LongTensor(self.buffer.actions)
        old_logprobs = torch.FloatTensor(self.buffer.logprobs)
        for _ in range(self.k_epochs):
            logprobs, state_values, dist_entropy = self.policy.evaluate(old_states, old_actions)
            ratios = torch.exp(logprobs - old_logprobs.detach())
            advantages = rewards - state_values.detach()
            surr1 = ratios*advantages
            surr2 = torch.clamp(ratios, 1-self.eps_clip, 1+self.eps_clip)*advantages
            loss = -torch.min(surr1, surr2) + 0.5*self.MseLoss(state_values, rewards) - 0.01*dist_entropy
            self.optimizer.zero_grad()
            loss.mean().backward()
            self.optimizer.step()
        self.policy_old.load_state_dict(self.policy.state_dict())
        self.buffer.clear()
    def step(self):
        self.timestep+=1
        if self.timestep%self.update_timestep==0:
            self.update()
            self.timestep=0
