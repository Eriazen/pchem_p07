from manim import *
import numpy as np
import random

class TrafficJamScene(Scene):
    def construct(self):
        # --- PARAMETERS ---
        CIRCLE_CENTER = 3.3 * LEFT
        GRAPH_ORIGIN = 4.2 * RIGHT

        CAR_COUNT = 25
        RADIUS = 3.5

        SPEED_LIMIT = 3.6
        ACCELERATION = 0.8

        BRAKING = 4.0
        BUMPER_TO_BUMPER = 0.1
        REACTION_TIME = 0.2

        HAZARD_FREQUENCY = 0.1
        FLUCTUATION = 0.1
        TIME = 50

        # --- SPACE-TIME DIAGRAM ---
        
        graph_axes = Axes(
            x_range=[0, 2*PI, PI/2],
            y_range=[0, TIME, 5],
            x_length=5,
            y_length=5,
            axis_config={"color": GRAY, "stroke_width": 2},
            tips=False
        ).move_to(GRAPH_ORIGIN)
        
        x_label = graph_axes.get_x_axis_label("Position", edge=DOWN, direction=DOWN, buff=0.2)
        y_label = graph_axes.get_y_axis_label("Time", edge=LEFT, direction=LEFT, buff=0.1).rotate(90*DEGREES)
        
        graph_title = Text("Time-Space Diagram", font_size=24).next_to(graph_axes, UP)
        
        self.add(graph_axes, x_label, y_label, graph_title)

        # --- ROAD VISUALS ---
        road = Circle(radius=RADIUS, color=GREY, stroke_width=25, stroke_opacity=0.3)
        road.move_to(CIRCLE_CENTER)

        self.add(road)

        # --- CAR OBJECTS ---
        # Data structure: [current_angle, speed]
        car_state = []
        car_mobs = VGroup()

        for i in range(CAR_COUNT):
            start_angle = (2 * PI / CAR_COUNT) * i
            
            car_symbol = RoundedRectangle(corner_radius=0.05, height=0.15, width=0.45, color=GREEN, fill_opacity=1)
            car_symbol.move_to(CIRCLE_CENTER + RADIUS * RIGHT)
            car_symbol.rotate(PI/2)
            car_symbol.rotate(start_angle, about_point=CIRCLE_CENTER)
            
            car_mobs.add(car_symbol)
            car_state.append([start_angle, 0.0])

        self.add(car_mobs)

        plot_dots = VGroup()
        self.add(plot_dots)

        # --- PHYSICS ENGINE ---
        time_tracker = ValueTracker(0)
        frame_tracker = ValueTracker(0)

        def update_sim(mob, dt):
            current_time = time_tracker.get_value()
            time_tracker.increment_value(dt)

            frames = frame_tracker.get_value()
            frame_tracker.increment_value(1)
            plot_frame = (int(frames) % 4 == 0)

            for i in range(CAR_COUNT):
                angle, speed = car_state[i]

                next_i = (i + 1) % CAR_COUNT
                angle_next, speed_next = car_state[next_i]

                diff_angle = angle_next - angle
                if diff_angle <= 0: diff_angle += 2 * PI
                distance = diff_angle * RADIUS

                gap = max(0.01, distance - 0.45)

                delta_v = speed - speed_next

                desired_gap = BUMPER_TO_BUMPER + (speed * REACTION_TIME) + (speed * delta_v) / (2*np.sqrt(ACCELERATION * BRAKING))

                free_road = 1 - (speed / SPEED_LIMIT)**4
                interaction = (desired_gap / gap)**2

                idm_accel = ACCELERATION * (free_road - interaction)

                speed += idm_accel * dt

                if random.random() < (HAZARD_FREQUENCY * dt):
                    if random.random() < 0.5:
                        speed *= 1-FLUCTUATION
                    else:
                        speed *= 1+FLUCTUATION
                
                if speed < 0: speed = 0
                if gap < 0.01: speed = 0

                # --- DATA STORAGE ---
                car_state[i][1] = speed
                delta_angle = (speed / RADIUS) * dt
                car_state[i][0] += delta_angle
                car_state[i][0] %= 2 * PI
                
                # --- VISUALS ---
                mob[i].rotate(delta_angle, about_point=CIRCLE_CENTER)

                norm_speed = speed / SPEED_LIMIT
                if norm_speed < 0.5:
                    c = interpolate_color(RED, YELLOW, norm_speed * 2)
                else:
                    c = interpolate_color(YELLOW, GREEN, (norm_speed - 0.5) * 2)
                mob[i].set_color(c)

                # --- PLOTTING ---
                if current_time < TIME and plot_frame:
                    if delta_angle < 1.0:
                        dot_pos = graph_axes.c2p(car_state[i][0], current_time)
                        
                        plot_point = Square(side_length=0.04, stroke_width=0, fill_color=c, fill_opacity=0.8)
                        plot_point.move_to(dot_pos)
                        plot_dots.add(plot_point)

        car_mobs.add_updater(update_sim)
        self.wait(TIME)