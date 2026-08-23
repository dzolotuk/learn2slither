from src.board.constants import (
    BOARD_SIZE, DIRECTIONS, OPPOSITE, UP, DOWN, LEFT, RIGHT)
from src.board.snake import Snake

import random


class Board:
    def __init__(self):
        self.reset()

    def reset(self):
        self.steps_without_food = 0

        self.green_apples = []
        self.red_apple = None

        self.current_direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.snake = self._create_snake(self.current_direction)

        self._spawn_green_apple()
        self._spawn_green_apple()
        self._spawn_red_apple()

    def _create_snake(self, direction):
        if direction == RIGHT:
            row = random.randint(0, BOARD_SIZE - 1)
            col = random.randint(2, BOARD_SIZE - 1)
            body = [
                (row, col),
                (row, col - 1),
                (row, col - 2),
            ]
        elif direction == LEFT:
            row = random.randint(0, BOARD_SIZE - 1)
            col = random.randint(0, BOARD_SIZE - 3)
            body = [
                (row, col),
                (row, col + 1),
                (row, col + 2),
            ]
        elif direction == UP:
            row = random.randint(2, BOARD_SIZE - 1)
            col = random.randint(0, BOARD_SIZE - 1)
            body = [
                (row, col),
                (row - 1, col),
                (row - 2, col),
            ]
        else:  # DOWN
            row = random.randint(0, BOARD_SIZE - 3)
            col = random.randint(0, BOARD_SIZE - 1)
            body = [
                (row, col),
                (row + 1, col),
                (row + 2, col),
            ]

        return Snake(body)

    def _get_free_cells(self):
        occupied = set(self.snake.body)

        occupied.update(self.green_apples)

        if self.red_apple:
            occupied.add(self.red_apple)

        free = []

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row, col) not in occupied:
                    free.append((row, col))

        return free

    def _spawn_green_apple(self):
        free = self._get_free_cells()

        if free:
            self.green_apples.append(
                random.choice(free)
            )

    def _spawn_red_apple(self):
        free = self._get_free_cells()

        if free:
            self.red_apple = random.choice(free)

    def get_grid(self):
        grid = [
            [0 for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]

        for row, col in self.green_apples:
            grid[row][col] = 1

        if self.red_apple:
            row, col = self.red_apple
            grid[row][col] = 2

        head_row, head_col = self.snake.head
        grid[head_row][head_col] = 3

        for row, col in self.snake.body[1:]:
            grid[row][col] = 4

        return grid

    def get_grid_safe(self):
        if not self.snake.body:
            return [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        return self.get_grid()

    def step(self, action):
        head = self.snake.head

        if action == OPPOSITE[self.current_direction]:
            action = self.current_direction

        self.current_direction = action
        dr, dc = DIRECTIONS[action]

        if head is None:
            return self._empty_state(), -100, True, "shrink"

        new_head = (head[0] + dr, head[1] + dc)

        alive_reward = -0.2
        green_reward = 25
        red_reward = -15
        death_reward = -50

        reward = alive_reward

        # wall collision
        if (
            new_head[0] < 0 or new_head[0] >= BOARD_SIZE or
            new_head[1] < 0 or new_head[1] >= BOARD_SIZE
        ):
            return self.get_state(), death_reward, True, "wall"

        will_eat_green = new_head in self.green_apples
        will_eat_red = new_head == self.red_apple

        if will_eat_green or will_eat_red:
            collision_body = self.snake.body
        else:
            collision_body = self.snake.body[:-1]

        if new_head in collision_body:
            return self.get_state(), death_reward, True, "body"

        if will_eat_green:
            self.snake.grow(new_head)
            self.green_apples.remove(new_head)
            self._spawn_green_apple()
            self.steps_without_food = 0
            self.current_direction = action
            reward = green_reward

        elif will_eat_red:
            self.snake.move(new_head)
            self.snake.shrink()
            self.red_apple = None
            self._spawn_red_apple()
            self.steps_without_food += 1
            self.current_direction = action
            reward = red_reward

        else:
            self.snake.move(new_head)
            self.steps_without_food += 1
            self.current_direction = action
            reward = alive_reward

        if self.snake.length() <= 0 or self.snake.head is None:
            return self._empty_state(), death_reward, True, "shrink"

        max_steps_without_food = 50

        if self.steps_without_food > max_steps_without_food:
            return (
                self.get_state(),
                death_reward,
                True,
                "starvation"
            )

        return self.get_state(), reward, False, None

    def _empty_state(self):
        return (0,) * 20

    def _scan_direction_features(self, start, direction):
        dr, dc = direction
        row, col = start

        wall_distance = 0
        green_seen = 0
        red_seen = 0
        body_seen = 0

        body_positions = set(self.snake.body[1:])

        while True:
            row += dr
            col += dc
            wall_distance += 1

            if row < 0 or row >= BOARD_SIZE or col < 0 or col >= BOARD_SIZE:
                break

            pos = (row, col)

            if pos in self.green_apples:
                green_seen = 1
            if pos == self.red_apple:
                red_seen = 1
            if pos in body_positions:
                body_seen = 1

        wall_close = 1 if wall_distance <= 2 else 0

        return (
            wall_close,
            green_seen,
            red_seen,
            body_seen,
        )

    def get_state(self):
        head = self.snake.head
        if head is None:
            return self._empty_state()

        up = self._scan_direction_features(head, (-1, 0))
        down = self._scan_direction_features(head, (1, 0))
        left = self._scan_direction_features(head, (0, -1))
        right = self._scan_direction_features(head, (0, 1))

        direction_state = (
            1 if self.current_direction == UP else 0,
            1 if self.current_direction == DOWN else 0,
            1 if self.current_direction == LEFT else 0,
            1 if self.current_direction == RIGHT else 0,
        )

        return (
            *up,
            *down,
            *left,
            *right,
            *direction_state,
        )
