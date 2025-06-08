"""Calculate the maximum friction brake you can use on your tackle.

This module provides functionality to calculate the maximum friction brake and tension
based on the reel's max drag, friction brake wear, leader's load capacity, and wear.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import sys

from rich import print
from rich.prompt import Prompt
from rich.table import Table

sys.path.append(".")
from rf4s import utils

BIAS = 1e-6


def get_tackle_stats():
    """Get actual stats of reel and leader based on their wears.

    Prompts the user for input and calculates the true max drag and load capacity
    after accounting for wear.

    :return: A tuple containing the true max drag and true load capacity.
    :rtype: tuple[float, float]
    """
    prompts = (
        "Reel's max drag (kg)",
        "Reel's friction brake wear (%)",
        "Leader's load capacity (kg)",
        "Leader's wear (%)",
    )

    while True:
        restart = False
        stats = []
        for prompt in prompts:
            validated_input = get_validated_input(prompt)
            if validated_input is None:
                restart = True
                break
            stats.append(validated_input)

        if restart:
            continue

        max_drag, friction_brake_wear, leader_load_capacity, leader_wear = stats
        true_max_drag = max_drag * (100 - friction_brake_wear) / 100
        true_load_capacity = leader_load_capacity * (100 - leader_wear) / 100
        return true_max_drag, true_load_capacity


def get_validated_input(prompt: str) -> float | None:
    """Get validated input from the user.

    Prompts the user for input and validates it. Supports quitting and restarting.

    :param prompt: The prompt message to display to the user.
    :type prompt: str
    :return: The validated input as a float, or None if the user chooses to restart.
    :rtype: float or None
    """
    while True:
        user_input = Prompt.ask(prompt)
        if user_input == "q":
            print("Bye.")
            sys.exit()
        if user_input == "r":
            return None

        try:
            return float(user_input)
        except ValueError:
            utils.print_error("Invalid input. Please enter a number.")


def main():
    """Main function to run the friction brake calculation.

    Prompts the user for input, calculates the result, and displays them in a table.
    """
    print("Please enter your tackle's stats, type q to quit, r to restart:")
    while True:
        max_drag, load_capacity = get_tackle_stats()
        max_friction_brake = int(min(load_capacity * 30 / (max_drag + BIAS) - 1, 29))
        max_tension = max_drag * max_friction_brake / 30

        table = Table(
            "Result",
            title="Your tackle's real stats 🎣",
            show_header=False,
            min_width=36,
        )
        table.add_row("Reel's true max drag", f"{max_drag:.2f} kg")
        table.add_row("Leader's true load capacity", f"{load_capacity:.2f} kg")
        table.add_row("Friction brake tension", f"{max_tension:.2f} kg")
        table.add_row("Maximum friction brake to use", f"{max_friction_brake}")
        print(table)


def run_app_from_main():
    main()


if __name__ == "__main__":
    main()
