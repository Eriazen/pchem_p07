import matplotlib.pyplot as plt
import numpy as np
import random
import math


RADIUS = 3.5
TRACK_LENGTH = 2 * math.pi * RADIUS

SPEED_LIMIT = 3.6
ACCELERATION = 0.8

BRAKING = 4.0
BUMPER_TO_BUMPER = 0.1
REACTION_TIME = 0.2

HAZARD_FREQUENCY = 0.05
FLUCTUATION = 0.05
DT = 1/60

SIMULATION_STEPS = 3000

def run_simulation(car_count):
    
    # Initialize cars: [angle, speed]
    car_state = np.zeros((car_count, 2))
    for i in range(car_count):
        car_state[i, 0] = (2 * math.pi / car_count) * i
        car_state[i, 1] = 0.0

    for step in range(SIMULATION_STEPS):
        current_snapshot = np.copy(car_state)
        
        for i in range(car_count):
            angle, speed = current_snapshot[i]

            next_i = (i + 1) % car_count
            angle_next, speed_next = current_snapshot[next_i]

            # --- PHYSICS ENGINE ---
            diff_angle = angle_next - angle
            if diff_angle <= 0: diff_angle += 2 * math.pi
            distance = diff_angle * RADIUS

            gap = max(0.01, distance - 0.45)

            delta_v = speed - speed_next

            desired_gap = BUMPER_TO_BUMPER + (speed * REACTION_TIME) + \
                          (speed * delta_v) / (2 * np.sqrt(ACCELERATION * BRAKING))

            free_road = 1 - (speed / SPEED_LIMIT)**4
            interaction = (desired_gap / gap)**2

            idm_accel = ACCELERATION * (free_road - interaction)

            speed += idm_accel * DT

            if random.random() < (HAZARD_FREQUENCY * DT):
                if random.random() < 0.5:
                    speed *= 1 - FLUCTUATION
                else:
                    speed *= 1 + FLUCTUATION
            
            if speed < 0: speed = 0
            if gap < 0.01: speed = 0

            # --- DATA STORAGE ---
            car_state[i][1] = speed
            delta_angle = (speed / RADIUS) * DT
            car_state[i][0] += delta_angle
            car_state[i][0] %= 2 * math.pi

    # --- CALCULATE METRICS ---
    density = car_count / TRACK_LENGTH
    avg_speed = np.mean(car_state[:, 1])
    flow = density * avg_speed
    
    return density, flow


if __name__ == "__main__":
    print("Simulating Fundamental Diagram...")
    
    densities = []
    flows = []
    
    for n in range(1, 41):
        k, q = run_simulation(n)
        densities.append(k)
        flows.append(q)
        print(f"Cars: {n:2d} | Density: {k:.2f} | Flow: {q:.2f}")

    # --- PLOTTING ---
    plt.figure(figsize=(10, 6))
    
    # Plot data points
    plt.scatter(densities, flows, c='k', zorder=2)
    plt.plot(densities, flows, 'k-', alpha=0.3, zorder=1)

    plt.xlabel("Hustota $k$ (vozidla / m)", fontsize=18)
    plt.ylabel("Dopravní tok $q$ (vozidla / s)", fontsize=18)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Annotation
    max_flow = max(flows)
    max_flow_index = flows.index(max_flow)
    critical_density = densities[max_flow_index]
    
    plt.axvline(critical_density, color='k', linestyle='--', label='Kritická hustota')
    
    plt.legend(fontsize=16)
    plt.savefig("fundamental_diagram.png", dpi=300, transparent=True)