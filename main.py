import argparse
from pathlib import Path

from src.agent.q_agent import QAgent
from src.training.trainer import Trainer


def parse_args():
    parser = argparse.ArgumentParser(
        description="Learn2Slither training and evaluation"
    )

    parser.add_argument(
        "--sessions",
        type=int,
        default=100,
        help="Number of training/evaluation sessions"
    )

    parser.add_argument(
        "--save",
        type=str,
        default=None,
        help="Path to save the model"
    )

    parser.add_argument(
        "--load",
        type=str,
        default=None,
        help="Path to load the model"
    )

    parser.add_argument(
        "--dontlearn",
        action="store_true",
        help="Run without learning"
    )

    parser.add_argument(
        "--visual",
        choices=["on", "off"],
        default="off",
        help="Enable or disable graphical display"
    )

    parser.add_argument(
        "--speed",
        type=int,
        default=200,
        help="Display speed in milliseconds"
    )

    parser.add_argument(
        "--step-by-step",
        action="store_true",
        help="Enable step-by-step mode"
    )

    parser.add_argument(
        "--max-duration",
        type=int,
        default=500,
        help="Maximum number of steps per session"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    agent = QAgent()

    if args.load:
        agent.load(args.load)
        print(f"Load trained model from {args.load}")

    trainer = Trainer(
        sessions=args.sessions,
        agent=agent,
        learn=not args.dontlearn,
        visual=(args.visual == "on"),
        speed_ms=args.speed,
        step_by_step=args.step_by_step,
        max_duration=args.max_duration,
    )

    trainer.train()

    if args.save:
        save_path = Path(args.save)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        agent.save(str(save_path))
        print(f"Save learning state in {args.save}")


if __name__ == "__main__":
    main()
