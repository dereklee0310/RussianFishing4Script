"""
Calculate the maximum friction brake you can use on your tackle.

Usage: calculate.py
"""


def get_tackle_stats() -> tuple[float, float]:
    """Get actual stats of reel and leader based on their wears.

    :return: reel's true max drag and leader's true load capacity
    :rtype: tuple[float, float]
    """
    max_drag = float(input("Reel's max drag (kg): "))
    friction_brake_wear = float(input("Reel's friction brake wear (%): "))
    leader_load_capacity = float(input("Leader's load capacity (kg): "))
    leader_wear = float(input("Leader's wear (%): "))

    true_max_drag = max_drag * (100 - friction_brake_wear)
    true_load_capacity = leader_load_capacity * (100 - leader_wear)
    return true_max_drag, true_load_capacity


if __name__ == "__main__":
    tmd, tlc = get_tackle_stats()
    max_friction_brake = int(min(tlc * 30 / tmd, 29))
    print(f"Maximum friction brake you can use: {max_friction_brake}")
