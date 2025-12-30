from manim import *
import numpy as np
import random

class TrafficJamScene(Scene):
    def construct(self):
        # --- PARAMETERS ---
        CIRCLE_CENTER = 3.0 * LEFT
        TEXT_POS = 4.0 * RIGHT

        CAR_COUNT = 25
        RADIUS = 3.66

        SPEED_LIMIT = 3.6
        ACCELERATION = 0.2

        BRAKING = 4.0
        BUMPER_TO_BUMPER = 0.02
        REACTION_TIME = 0.2

        HAZARD_FREQUENCY = 0.1
        HAZARD_CHANGE = 0.1
        TIME = 50

        # --- DASHBOARD ---
        def create_param_text(label, value, color=WHITE):
            row = VGroup(
                Text(label, font_size=24, color=color),
                Text(str(value), font_size=24, color=color, font="Monospace")
            ).arrange(RIGHT, buff=0.5)
            return row

        title = Text("Parameters", font_size=32, weight=BOLD).move_to(TEXT_POS + 3*UP)
        underline = Line(LEFT, RIGHT, color=WHITE).next_to(title, DOWN).scale(0.8)
        
        param_group = VGroup(
            create_param_text("Car Count:", CAR_COUNT),
            create_param_text("Speed Limit:", f"{SPEED_LIMIT*10} m/s"),
            create_param_text("Acceleration:", f"{ACCELERATION*10} m/s²"),
            create_param_text("Reaction Time:", f"{REACTION_TIME*10} s"),
            create_param_text("Still Distance:", f"{BUMPER_TO_BUMPER*10} m"),
            create_param_text("Braking Default:", f"{BRAKING*10} m/s²"),
            create_param_text("Hazard Frequency:", f"{HAZARD_FREQUENCY}"),
            create_param_text("Speed Change:", f"{HAZARD_CHANGE}"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4).next_to(underline, DOWN, buff=0.5)
        
        full_panel = VGroup(title, underline, param_group)
        full_panel.move_to(TEXT_POS)
        
        self.add(full_panel)

        # --- ROAD VISUALS ---
        road = Circle(radius=RADIUS, color=GREY, stroke_width=25, stroke_opacity=0.3)
        road.move_to(CIRCLE_CENTER)
        #line = Circle(radius=RADIUS, color=WHITE, stroke_width=2, stroke_opacity=0.5)
        #line.move_to(CIRCLE_CENTER)
        self.add(road)

        # --- OBJEKTY AUT ---
        # Data structure: [current_angle, speed, slowdown_magnitude]
        car_state = []
        car_mobs = VGroup()

        for i in range(CAR_COUNT):
            start_angle = (2 * PI / CAR_COUNT) * i
            
            car_symbol = RoundedRectangle(corner_radius=0.05, height=0.15, width=0.35, color=GREEN, fill_opacity=1)
            car_symbol.move_to(CIRCLE_CENTER + RADIUS * RIGHT)
            car_symbol.rotate(PI/2)
            car_symbol.rotate(start_angle, about_point=CIRCLE_CENTER)
            
            car_mobs.add(car_symbol)
            car_state.append([start_angle, 0.0])

        self.add(car_mobs)

        # --- FYZIKÁLNÍ ENGINE ---
        def update_sim(mob, dt):
            
            for i in range(CAR_COUNT):
                angle, speed = car_state[i]
                
                next_i = (i + 1) % CAR_COUNT
                angle_next, _ = car_state[next_i]
                
                diff_angle = angle_next - angle
                if diff_angle <= 0: diff_angle += 2 * PI
                distance = diff_angle * RADIUS
                
                gap = max(0.01, distance - 0.2)
                safe_distance = BUMPER_TO_BUMPER + (speed * REACTION_TIME)

                if gap > safe_distance:
                    if speed < SPEED_LIMIT:
                        speed += ACCELERATION * dt
                else:
                    kinematic_req = (speed ** 2)/(2*safe_distance)
                    ratio = safe_distance / gap
                    panic_factor = np.exp(ratio-1)
                    braking_force = kinematic_req * panic_factor
                    braking_force = min(braking_force, 40.0)
                    speed -= braking_force * dt
                
                if random.random() < (HAZARD_FREQUENCY * dt):
                    if random.random() < 0.5:
                        speed *= 1-HAZARD_CHANGE
                    else:
                        speed *= 1+HAZARD_CHANGE
                
                speed = max(0, min(speed, SPEED_LIMIT * 1.05))
                
                # --- DATA STORAGE ---
                car_state[i][1] = speed
                delta_angle = (speed / RADIUS) * dt
                car_state[i][0] += delta_angle
                car_state[i][0] %= 2 * PI
                
                # --- VISUALS ---
                mob[i].rotate(delta_angle, about_point=CIRCLE_CENTER)
                
                # Colors
                norm_speed = speed / SPEED_LIMIT
                if norm_speed < 0.5:
                    c = interpolate_color(RED, YELLOW, norm_speed * 2)
                else:
                    c = interpolate_color(YELLOW, GREEN, (norm_speed - 0.5) * 2)
                mob[i].set_color(c)

        car_mobs.add_updater(update_sim)
        self.wait(TIME)