"""
Calculate the maximum friction brake you can use without breaking the tackle.

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
    return max_drag * (100 - friction_brake_wear), leader_load_capacity * (100 - leader_wear)


if __name__ == '__main__':
    tmd, tlc = get_tackle_stats()
    print(f'Maximum friction brake you can use: {int(min(tlc * 30 / tmd, 29))}')