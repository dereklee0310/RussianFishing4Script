friction_brake_wear = float(input('Friction Brake Wear:'))
max_drag = 7.7 * (100 - friction_brake_wear)

leader_wear = float(input('Leader Wear:'))
max_leader_load = 6.4 * (100 - leader_wear)

print('Max friction brake: ', min(max_leader_load * 30 / max_drag, 29))