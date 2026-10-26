# Learn2Slither 🐍

A **Snake agent that learns to play by itself with tabular Q-learning**, implemented from scratch in Python.

The snake only sees what lies in the four directions from its head. From that limited view, it learns through trial and error to eat green apples, avoid red apples, and not crash into walls or its own body.

> 42 Paris project — reinforcement learning.

---

## Table of contents

- [Game rules](#game-rules)
- [Installation](#installation)
- [Usage](#usage)
- [Pretrained models](#pretrained-models)
- [How it works](#how-it-works)
  - [State: what the snake sees](#state-what-the-snake-sees)
  - [Rewards](#rewards)
  - [Q-learning](#q-learning)
- [Project structure](#project-structure)
- [Tech stack](#tech-stack)

---

## Game rules

- **Board:** 10 × 10.
- **Snake:** starts with a length of 3, at a random position and in a random direction.
- **Apples:** 2 green and 1 red on the board at all times. An eaten apple immediately respawns on a free cell.
  - 🟢 **Green apple:** length +1.
  - 🔴 **Red apple:** length −1.
- **Actions:** `UP`, `DOWN`, `LEFT`, `RIGHT`. Choosing the direction opposite to the current one keeps the snake going straight.
- **Game over** when the snake:
  - hits a wall,
  - hits its own body,
  - shrinks to a length of 0,
  - goes more than 50 moves without eating a green apple (starvation),
  - or reaches the maximum number of moves per session (`--max-duration`).

---

## Installation

```bash
git clone https://github.com/dzolotuk/learn2slither.git
cd learn2slither
./setup.sh
source local_env/bin/activate
```

`setup.sh` creates a virtual environment `local_env` and installs `numpy`, `pygame` and `flake8`.

Run all commands **from the repository root**.

---

## Usage

Everything goes through `main.py`.

**Train a new agent and save it:**

```bash
python3 main.py --sessions 1000 --save models/1000.json
```

**Watch a trained agent play, without learning:**

```bash
python3 main.py --load models/10000.json --sessions 10 --dontlearn --visual on --speed 100
```

**Go move by move** (press <kbd>Space</kbd> for the next move):

```bash
python3 main.py --load models/10000.json --sessions 1 --dontlearn --visual on --step-by-step
```

**Continue training an existing model:**

```bash
python3 main.py --load models/1000.json --sessions 500 --save models/1500.json
```

### Options

| Option | Default | Description |
|---|---|---|
| `--sessions` | `100` | Number of games to play |
| `--save PATH` | — | Save the Q-table to a JSON file at the end |
| `--load PATH` | — | Load a Q-table from a JSON file before starting |
| `--dontlearn` | off | Play greedily with the current Q-table: no exploration, no updates |
| `--visual on\|off` | `off` | Show the board in a pygame window |
| `--speed MS` | `200` | Time per move in milliseconds (with `--visual on`) |
| `--step-by-step` | off | Wait for <kbd>Space</kbd> after each move (with `--visual on`) |
| `--max-duration` | `500` | Maximum number of moves per session |

### Console output

One line per session:

```
Session 42/100 | Length=7 | Duration=118 | States=1534 | Epsilon=0.0500
```

Then a summary at the end:

```
Training finished | Best length=... | Best duration=... | Wall deaths=... | Shrink deaths=... | Body deaths=... | Starvation deaths=... | Repeated states penalties=...
```

### Display colours

| Colour | Meaning |
|---|---|
| 🟦 Dark blue | Snake head |
| 🩵 Light blue | Snake body |
| 🟩 Green | Green apple |
| 🟥 Red | Red apple |

---

## Pretrained models

The `models/` folder contains Q-tables saved after different numbers of training sessions:

| File | Sessions | States in Q-table | ε at save time |
|---|---|---|---|
| `models/10.json` | 10 | 35 | 0.97 |
| `models/100.json` | 100 | 247 | 0.74 |
| `models/1000.json` | 1 000 | 1 698 | 0.05 |
| `models/10000.json` | 10 000 | 4 431 | 0.05 |

Comparing them with `--dontlearn --visual on` shows how the behaviour improves with training.

---

## How it works

### State: what the snake sees

The snake has no view of the whole board. From its head, it looks in each of the four directions up to the wall. For each direction, it records 4 binary values:

| Feature | Value 1 if… |
|---|---|
| `wall_close` | the wall is at most 2 cells away |
| `green_seen` | there is a green apple somewhere in that direction |
| `red_seen` | there is a red apple somewhere in that direction |
| `body_seen` | there is a part of its body somewhere in that direction |

To these 4 × 4 = 16 values, the state adds the current direction as a one-hot vector of 4 values. The state is therefore a tuple of **20 binary values**, used directly as a key in the Q-table.

### Rewards

| Event | Reward |
|---|---|
| Ordinary move | −0.2 |
| Eating a green apple | +25 |
| Eating a red apple | −15 |
| Death (wall, body, length 0, starvation) | −50 |
| Reaching a state already seen in the last 20 moves | an extra −0.5 × number of repeats |

The small penalty for each move and the penalty for repeated states discourage the snake from wandering in circles.

### Q-learning

The agent keeps a table `Q[state][action]` and updates it after each move:

```
Q(s, a) ← Q(s, a) + α · [ r + γ · max_a' Q(s', a') − Q(s, a) ]
```

On a final move, the target is just `r`.

| Hyperparameter | Value |
|---|---|
| Learning rate α | 0.1 |
| Discount factor γ | 0.95 |
| Initial ε | 1.0 |
| Minimum ε | 0.05 |
| ε decay | ×0.997 after each session |

Exploration follows an **ε-greedy** policy: with probability ε, the agent picks a random action, otherwise the action with the highest Q-value. ε reaches its minimum after about 1 000 sessions. In a state the agent has never seen, it always plays at random.

A saved model is a JSON file containing the hyperparameters, the current ε and the full Q-table. When a model is loaded, its ε is restored too, so training resumes where it left off.

---

## Project structure

```
learn2slither/
├── main.py                  # entry point: CLI arguments, load / train / save
├── setup.sh                 # venv + dependencies
├── models/                  # pretrained Q-tables (JSON)
└── src/
    ├── board/
    │   ├── constants.py     # board size, directions
    │   ├── snake.py         # Snake: move, grow, shrink
    │   └── board.py         # game rules, rewards, state computation
    ├── agent/
    │   └── q_agent.py       # QAgent: ε-greedy, Q-learning update, save/load
    ├── training/
    │   └── trainer.py       # session loop, statistics
    └── ui/
        └── renderer.py      # pygame display, step-by-step mode
```

---

## Tech stack

Python 3 · pygame · flake8

## Author

- [Dmytro Zolotukhin](https://github.com/dzolotuk) — 42 Paris
