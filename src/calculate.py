"""
Calculate the maximum friction brake you can use on your tackle.

Usage: calculate.py
"""

import logging

def get_tackle_stats():
    """Get actual stats of reel and leader based on their wears."""
    while True:
        try:
            max_drag = float(input("Reel's max drag (kg): "))
            if max_drag <= 0:
                print("Max drag should be a positive number.")
                continue

            friction_brake_wear = float(input("Reel's friction brake wear (%): "))
            if not (0 <= friction_brake_wear <= 100):
                print("Friction brake wear should be between 0 and 100.")
                continue

            leader_load_capacity = float(input("Leader's load capacity (kg): "))
            if leader_load_capacity <= 0:
                print("Leader's load capacity should be a positive number.")
                continue

            leader_wear = float(input("Leader's wear (%): "))
            if not (0 <= leader_wear <= 100):
                print("Leader's wear should be between 0 and 100.")
                continue

            true_max_drag = max_drag * (100 - friction_brake_wear) / 100
            true_load_capacity = leader_load_capacity * (100 - leader_wear) / 100
            return true_max_drag, true_load_capacity

        except ValueError:
            print("Invalid input. Please enter numeric values.")

def calculate_friction_brake(true_max_drag, true_load_capacity):
    """Calculate the maximum friction brake you can use and its tension."""
    max_friction_brake = int(min(true_load_capacity * 30 / true_max_drag, 29))
    friction_brake_tension = true_max_drag * max_friction_brake / 100
    return max_friction_brake, friction_brake_tension

def main():
    # Set up logging configuration once at the beginning
    logging.basicConfig(level=logging.WARNING)

    while True:
        # Get the true max drag and true load capacity
        print("--- Input Your Tackle Stats ---")
        true_max_drag, true_load_capacity = get_tackle_stats()

        # Calculate the maximum friction brake and its tension
        max_friction_brake, friction_brake_tension = calculate_friction_brake(true_max_drag, true_load_capacity)

        # Display results
        print(f"\nReel's true max drag: {true_max_drag:.2f} kg")
        print(f"Leader's true load capacity: {true_load_capacity:.2f} kg")
        print(f"Maximum friction brake setting: {max_friction_brake}")
        print(f"Friction brake tension: {friction_brake_tension:.2f} kg")

        # Check if the friction brake is safe for the leader
        if friction_brake_tension >= true_load_capacity:
            logging.warning("Warning: The leader may break with this friction brake setting.")

        # Additional messages
        print("\nTip: Always ensure the friction brake tension is below the leader's capacity.", end="\n\n")
        print("Thank you for using the Friction Brake Calculator!\n")

        # Ask if the user wants to restart or exit
        ans = input("Would you like to restart the calculation? [Y/n] ").strip().lower()
        if ans == "n":
            break  # Exiting the loop

if __name__ == "__main__":
    main()