"""
Calculate the maximum friction brake you can use on your tackle.

Usage: calculate.py
"""

def get_tackle_stats():
    """Get actual stats of reel and leader based on their wears."""
    try:
        max_drag = float(input("Reel's max drag (kg): "))
        friction_brake_wear = float(input("Reel's friction brake wear (%): "))
        leader_load_capacity = float(input("Leader's load capacity (kg): "))
        leader_wear = float(input("Leader's wear (%): "))

        true_max_drag = max_drag * (100 - friction_brake_wear) / 100
        true_load_capacity = leader_load_capacity * (100 - leader_wear) / 100
        return true_max_drag, true_load_capacity
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        return get_tackle_stats()

def calculate_friction_brake(true_max_drag, true_load_capacity):
    """Calculate the maximum friction brake you can use and its strength."""
    max_friction_brake = int(min(true_load_capacity * 30 / true_max_drag, 29))
    friction_brake_strength = true_max_drag * max_friction_brake / 100
    return max_friction_brake, friction_brake_strength

def main():
    while True:
        # Get the true max drag and true load capacity
        print("--- Input Your Tackle Stats ---")
        true_max_drag, true_load_capacity = get_tackle_stats()

        # Calculate the maximum friction brake and its strength
        max_friction_brake, friction_brake_strength = calculate_friction_brake(true_max_drag, true_load_capacity)

        # Display results
        print("\n--- Results ---")
        print(f"Reel's true max drag: {true_max_drag:.2f} kg")
        print(f"Leader's true load capacity: {true_load_capacity:.2f} kg")
        print(f"Maximum friction brake setting: {max_friction_brake}")
        print(f"Strength of the friction brake: {friction_brake_strength:.2f} kg")

        # Check if the friction brake is safe for the leader
        safety_check_message = "The leader is safe with this friction brake setting."
        if friction_brake_strength < true_load_capacity:
            safety_check_message = "The leader is safe with this friction brake setting."
        else:
            safety_check_message = "Warning: The leader may break with this friction brake setting."

        print(safety_check_message)

        # Additional messages
        tip_message = "\nTip: Always ensure the friction brake strength is below the leader's capacity."
        print(tip_message)
        print("\nThank you for using the Friction Brake Calculator!")

        # Ask if the user wants to restart or exit
        restart = input("\nWould you like to restart the calculation? (yes/no): ").strip().lower()
        if restart != "yes":
            break


if __name__ == "__main__":
    main()