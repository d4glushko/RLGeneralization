import typing
import numpy as np
import matplotlib
matplotlib.use("TKAgg")
import matplotlib.pyplot as plt
from enum import Enum

from .agents.base_agent import BaseAgent
from .agents.a2c_agent import A2CAgent
from .agents.dqn_agent import DqnAgent
from .envs.env import EnvironmentWrapper
from .metrics_manager import MetricsManager, Metric


class NoiseLearningAgents(Enum):
    DQN = 1
    A2C = 2
    

class NoiseLearning:
    def __init__(
        self, agents_number: int, env_name: str, noise_learning_agent: NoiseLearningAgents, debug: bool, 
        metrics_number_of_elements: int, metrics_number_of_iterations: int, noise_env_step: float
    ):
        self.agents_number: int = agents_number
        self.environments: typing.List[EnvironmentWrapper] = [
            EnvironmentWrapper(env_name, noise_std_dev=(i * noise_env_step)) for i in range(agents_number)
        ]
        self.agents: typing.List[BaseAgent] = [
            self.__choose_agent(noise_learning_agent)(env.observation_space(), env.action_space(), debug)
            for env in [
                self.environments[i]
                for i in range(agents_number)
            ]
        ]
        self.metrics: typing.List[MetricsManager] = [
            MetricsManager(metrics_number_of_elements, metrics_number_of_iterations) for i in range(agents_number)
        ]

    def __choose_agent(self, noise_learning_agent: NoiseLearningAgents) -> typing.Type[BaseAgent]:
        agents_mapping = {
            NoiseLearningAgents.DQN: DqnAgent,
            NoiseLearningAgents.A2C: A2CAgent
        }
        return agents_mapping[noise_learning_agent]

    def train(self, training_episodes):
        for i in range(1, training_episodes + 1):
            print(f"Episode {i}. {((i / training_episodes) * 100):.2f}% done")
            for j in range(self.agents_number):
                agent = self.agents[j]
                env = self.environments[j]
                metrics = self.metrics[j]

                state = env.reset()

                # TODO: code is bound to the CartPole env currently. Make it more env agnostic
                score = 0
                while True:
                    # env.render()
                    score += 1

                    action = agent.act(state)
                    state_next, reward, done, info = env.step(action)
                    
                    if done:
                        reward = -reward
                        state_next = None
                    
                    agent.remember(state, action, reward, done, state_next)
                    agent.reflect()
                    metrics.add_loss(agent.last_loss, i)

                    if done:
                        break

                    state = state_next
                metrics.add_score(score, i)
                print(f"Agent {j} finished. Score {score}")

            if self.should_swap_agents():
                self.swap_agents()

    def show_metrics(self):
        self.__plot_scores()
        self.__plot_losses()
        plt.show(block=False)

    def __plot_scores(self):
        fig = plt.figure()
        legend = []
        for i in range(self.agents_number):
            metrics = self.metrics[i]
            noise = self.environments[i].noise_std_dev
            avgs: typing.List[Metric] = metrics.get_mov_avg_scores()
            plt.plot([avg.iteration for avg in avgs], [avg.value for avg in avgs])
            legend.append(f"Agent {i}, Current Noise = {noise:.2f}")
            
        fig.suptitle(f"Score")
        plt.ylabel(f"Moving avg over the last {metrics.number_of_elements} elements every {metrics.number_of_iterations} iterations")
        plt.xlabel(f"Env Iterations")
        plt.legend(legend, loc='upper left')
    
    def __plot_losses(self):
        fig = plt.figure()
        legend = []
        for i in range(self.agents_number):
            metrics = self.metrics[i]
            noise = self.environments[i].noise_std_dev
            avgs: typing.List[Metric] = metrics.get_mov_avg_losses()
            plt.plot([avg.iteration for avg in avgs], [avg.value for avg in avgs])
            legend.append(f"Agent {i}, Current Noise = {noise:.2f}")
            
        fig.suptitle(f"Loss")
        plt.ylabel(f"Moving avg over the last {metrics.number_of_elements} elements every {metrics.number_of_iterations} iterations")
        plt.xlabel(f"Env Iterations")
        plt.legend(legend, loc='upper left')

    def should_swap_agents(self):
        pass

    def swap_agents(self):
        pass
