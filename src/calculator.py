"""
Calculate the maximum friction brake you can use without breaking the tackle.

Usage: calculator.py 

Todo: use argv as input
"""

def get_reel_TMD():
    """
    Calculate the reel's true max drag based on user input.

    :returns: reel's true max drag
    """
    max_drag = float(input("Reel's max drag (kg): "))
    friction_brake_wear = float(input("Reel's friction brake wear (%): "))
    return max_drag * (100 - friction_brake_wear)

def get_leader_TLC():
    """
    Calculate the leader's true load capacity based on user input.

    :returns: leader's true load capacity
    """ 
    leader_load_capacity = float(input("Leader's load capacity (kg): "))
    leader_wear = float(input("Leader's wear (%): "))
    return leader_load_capacity * (100 - leader_wear)

if __name__ == '__main__':
    tmd, tlc = get_reel_TMD(), get_leader_TLC()
    print(f'Max friction brake: {int(min(tlc * 30 / tmd, 29))}')