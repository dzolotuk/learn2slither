from src.board.board import Board
from src.agent.q_agent import QAgent
from src.ui.renderer import Renderer


class Trainer:
    def __init__(
            self,
            sessions=100,
            agent=None,
            learn=True,
            visual=False,
            speed_ms=200,
            step_by_step=False,
            max_duration=200
    ):
        self.sessions = sessions
        self.board = Board()
        self.agent = agent if agent is not None else QAgent()
        self.learn = learn
        self.max_duration = max_duration

        self.renderer = None

        if visual:
            self.renderer = Renderer(
                speed_ms=speed_ms,
                step_by_step=step_by_step
            )

    def train(self):
        best_length = 0
        best_duration = 0
        repeat_penalties = 0

        wall_deaths = 0
        body_deaths = 0
        shrink_deaths = 0
        starvation_deaths = 0

        total_length = 0
        total_duration = 0

        for session in range(1, self.sessions + 1):
            self.board.reset()

            if self.renderer:
                if not self.renderer.draw(self.board.get_grid_safe()):
                    return

            state = self.board.get_state()
            recent_states = []
            game_over = False
            duration = 0

            while not game_over and duration < self.max_duration:
                action = self.agent.choose_action(state, explore=self.learn)

                next_state, reward, game_over, reason = self.board.step(action)

                repeat_count = recent_states.count(next_state)

                if repeat_count > 0:
                    reward -= repeat_count * 0.5
                    repeat_penalties += 1

                recent_states.append(next_state)

                if len(recent_states) > 20:
                    recent_states.pop(0)

                if self.renderer:
                    if not self.renderer.draw(self.board.get_grid_safe()):
                        return

                if reason == "wall":
                    wall_deaths += 1
                elif reason == "body":
                    body_deaths += 1
                elif reason == "shrink":
                    shrink_deaths += 1
                elif reason == "starvation":
                    starvation_deaths += 1

                if self.learn:
                    self.agent.update(
                        state,
                        action,
                        reward,
                        next_state,
                        game_over
                    )

                state = next_state
                duration += 1

            if self.learn:
                self.agent.decay_epsilon()

            length = self.board.snake.length()
            total_length += length
            total_duration += duration

            best_length = max(best_length, length)
            best_duration = max(best_duration, duration)

            print(
                f"Session {session}/{self.sessions} | "
                f"Length={length} | "
                f"Duration={duration} | "
                f"States={self.agent.states_count()} | "
                f"Epsilon={self.agent.epsilon:.4f}"
            )

        if self.renderer:
            self.renderer.close()

        print()
        print(
            f"Training finished | "
            f"Best length={best_length} | "
            f"Best duration={best_duration} | "
            f"Wall deaths={wall_deaths} | "
            f"Shrink deaths={shrink_deaths} | "
            f"Body deaths={body_deaths} | "
            f"Starvation deaths={starvation_deaths} | "
            f"Repeated states penalties={repeat_penalties}"
        )
