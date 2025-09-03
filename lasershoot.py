import matplotlib.pyplot as plt
import numpy as np
import random
from shapely.geometry import LineString

# Box dimensions in cm
WIDTH = 56
HEIGHT = 35
CELL_W = WIDTH / 3
CELL_H = HEIGHT / 3

def draw_grid(ax):
    for i in range(4):
        ax.plot([0, WIDTH], [i * CELL_H, i * CELL_H], color='black')
        ax.plot([i * CELL_W, i * CELL_W], [0, HEIGHT], color='black')
    ax.axhline(HEIGHT / 2, color='darkred', linewidth=2)

def place_laser(ax):
    ax.arrow(-3, HEIGHT / 2, 3, 0, head_width=1, head_length=2, color='darkred')

def generate_barrier(center_x, center_y, angle, length):
    dx = (length / 2) * np.cos(np.radians(angle))
    dy = (length / 2) * np.sin(np.radians(angle))
    x1, y1 = center_x - dx, center_y - dy
    x2, y2 = center_x + dx, center_y + dy
    return (x1, y1, x2, y2), LineString([(x1, y1), (x2, y2)])

def place_barrier(ax, barrier_line, is_mirror=False, angle=0, mirror_facing=1):
    x1, y1, x2, y2 = barrier_line
    ax.plot([x1, x2], [y1, y2], color='cyan' if is_mirror else 'black', linewidth=2)

    if is_mirror:
        # Midpoint
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        # Perpendicular vector for tick mark (flip based on mirror facing)
        nx = -np.sin(np.radians(angle)) * mirror_facing
        ny = np.cos(np.radians(angle)) * mirror_facing
        ax.plot([mx, mx - 1.5 * nx], [my, my - 1.5 * ny], color='blue', linewidth=1.5)

def choose_target_point():
    x_target = WIDTH
    y_target = random.uniform(0, 30)
    return x_target, y_target

def generate_non_overlapping_barriers():
    placed = []
    attempts = 0
    max_attempts = 300

    mirror_index = random.randint(0, 2)
    center_line_index = random.randint(0, 2)

    while len(placed) < 3 and attempts < max_attempts:
        idx = len(placed)
        is_mirror = (idx == mirror_index)
        must_touch_center_line = (idx == center_line_index)
        length = 5 if is_mirror else 8
        angle = random.uniform(0, 180)

        success = False
        for _ in range(30):  # Try multiple placements
            # Handle mirror spacing constraints
            if is_mirror:
                min_x = 8 + length / 2
                max_x = WIDTH - 3 - length / 2
            else:
                min_x = length / 2
                max_x = WIDTH - length / 2

            x = random.uniform(min_x, max_x)
            y = random.uniform(length / 2, HEIGHT - length / 2)

            (x1, y1, x2, y2), shape = generate_barrier(x, y, angle, length)

            # Must touch center line?
            if must_touch_center_line:
                center_line = LineString([(0, HEIGHT / 2), (WIDTH, HEIGHT / 2)])
                if shape.distance(center_line) > 0.1:
                    continue

            # Avoid overlap
            if all(shape.distance(existing[1]) > 0.5 for existing in placed):
                facing = random.choice([-1, 1]) if is_mirror else None
                placed.append(((x1, y1, x2, y2), shape, is_mirror, angle, facing))
                success = True
                break

        if not success:
            attempts += 1

    return placed

def draw_box():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_aspect('equal')
    ax.set_xlim(-5, WIDTH + 5)
    ax.set_ylim(-5, HEIGHT + 5)
    ax.axis('off')

    draw_grid(ax)
    place_laser(ax)

    barriers = generate_non_overlapping_barriers()
    for (x1, y1, x2, y2), _, is_mirror, angle, facing in barriers:
        place_barrier(ax, (x1, y1, x2, y2), is_mirror=is_mirror, angle=angle, mirror_facing=facing if is_mirror else 1)

    # Place target
    x_target, y_target = choose_target_point()
    ax.plot(x_target, y_target, 'ro')
    ax.text(x_target + 2, y_target, f'Target\n({round(y_target,1)} cm)', va='center')

    plt.tight_layout()
    plt.show()
draw_box()
