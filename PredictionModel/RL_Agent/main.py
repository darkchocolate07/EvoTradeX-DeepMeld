import gym
import numpy as np
from RL.agent import PPO
from RL.environment import CustomEnv

def run():
    env = CustomEnv()
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    ppo_agent = PPO(state_dim, action_dim, lr=0.002, gamma=0.99, eps_clip=0.2, update_timestep=2000, k_epochs=10)
    max_episodes = 1000
    for ep in range(max_episodes):
        state = env.reset()
        done=False
        while not done:
            action, logprob = ppo_agent.select_action(state)
            next_state, reward, done, _ = env.step(action)
            ppo_agent.buffer.add(state, action, logprob, reward, done)
            state = next_state
            ppo_agent.step()
if __name__=="__main__":
    run()
