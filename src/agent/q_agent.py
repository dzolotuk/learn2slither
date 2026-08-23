import json
import random
from collections import defaultdict

from src.board.constants import UP, DOWN, LEFT, RIGHT


class QAgent:
    def __init__(
        self,
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon=1.0,
        epsilon_min=0.05,
        epsilon_decay=0.997
    ):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        self.actions = [UP, DOWN, LEFT, RIGHT]

        self.q_table = defaultdict(
            lambda: {a: 0.0 for a in self.actions}
        )

    def _state_key(self, state):
        return json.dumps(state)

    def _restore_state(self, obj):
        if isinstance(obj, list):
            return tuple(self._restore_state(item) for item in obj)
        return obj

    def choose_action(self, state, explore=True):
        q_values = self.q_table.get(state)

        if q_values is None:
            return random.choice(self.actions)

        if explore and random.random() < self.epsilon:
            return random.choice(self.actions)

        return max(q_values, key=q_values.get)

    def update(self, state, action, reward, next_state, done):
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in self.actions}
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0.0 for a in self.actions}

        current = self.q_table[state][action]

        if done:
            target = reward
        else:
            next_max = max(self.q_table[next_state].values())
            target = reward + self.discount_factor * next_max

        self.q_table[state][action] += self.learning_rate * (target - current)

    def decay_epsilon(self):
        self.epsilon = max(
            self.epsilon_min,
            self.epsilon * self.epsilon_decay
        )

    def states_count(self):
        return len(self.q_table)

    def save(self, path):
        data = {
            "learning_rate": self.learning_rate,
            "discount_factor": self.discount_factor,
            "epsilon": self.epsilon,
            "epsilon_min": self.epsilon_min,
            "epsilon_decay": self.epsilon_decay,
            "q_table": {
                self._state_key(state): values
                for state, values in self.q_table.items()
            }
        }

        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file)

    def load(self, path):
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.learning_rate = data.get("learning_rate", self.learning_rate)
        self.discount_factor = data.get(
            "discount_factor", self.discount_factor)
        self.epsilon = data.get("epsilon", self.epsilon)
        self.epsilon_min = data.get("epsilon_min", self.epsilon_min)
        self.epsilon_decay = data.get("epsilon_decay", self.epsilon_decay)

        self.q_table = defaultdict(
            lambda: {a: 0.0 for a in self.actions}
        )

        for state_key, values in data.get("q_table", {}).items():
            state = self._restore_state(json.loads(state_key))
            self.q_table[state] = {
                action: float(values.get(action, 0.0))
                for action in self.actions
            }
