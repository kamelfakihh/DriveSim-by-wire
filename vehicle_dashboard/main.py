import pygame
import sys
import math
from kuksa_client.grpc import VSSClient
from threading import Thread, Lock
import os
# Initialize Pygame
pygame.init()
# Screen dimensions
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vehicle Dashboard")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

# Font
font = pygame.font.SysFont("Arial", 24)

# Shared vehicle values and lock
values = {"speed": 0, "brake": 0, "acceleration": 0, "steering_angle": 0,'anamoly':False}
anomaly_count = 0
speed_lock = Lock()

# Utility function to draw a needle for steering angle
def draw_needle(center, angle, radius, color=RED):
    # Adjust the angle to start 0 degrees at the top (90 degrees in conventional orientation)
    adjusted_angle = angle + 90
    radians = math.radians(adjusted_angle)
    end_x = center[0] + radius * math.cos(radians)
    end_y = center[1] - radius * math.sin(radians)
    pygame.draw.line(screen, color, center, (end_x, end_y), 2)

# Kuksa client thread to fetch vehicle data
def start_kuksa_client():
    global anomaly_count
    try:
        broker_address = os.getenv('BROKER_ADDRESS','127.0.0.1')
        broker_port = int(os.getenv('BROKER_PORT','55555'))
        with VSSClient(broker_address, broker_port) as client:
            # Subscribe to vehicle parameters
            for updates in client.subscribe_current_values(['Vehicle.Speed', 
                                                            'Vehicle.Chassis.Brake.PedalPosition', 
                                                            'Vehicle.Chassis.Accelerator.PedalPosition', 
                                                            'Vehicle.Chassis.Axle.Row1.SteeringAngle',
                                                            'Vehicle.Analytics.Anamoly']):
                with speed_lock:
                    # Update speed
                    if updates.get('Vehicle.Speed') and updates['Vehicle.Speed'].value:
                        values["speed"] = updates['Vehicle.Speed'].value

                    # Update brake
                    if updates.get('Vehicle.Chassis.Brake.PedalPosition') and updates['Vehicle.Chassis.Brake.PedalPosition'].value:
                        values["brake"] = updates['Vehicle.Chassis.Brake.PedalPosition'].value

                    # Update acceleration (throttle)
                    if updates.get('Vehicle.Chassis.Accelerator.PedalPosition') and updates['Vehicle.Chassis.Accelerator.PedalPosition'].value:
                        values["acceleration"] = updates['Vehicle.Chassis.Accelerator.PedalPosition'].value

                    # Update steering angle
                    if updates.get('Vehicle.Chassis.Axle.Row1.SteeringAngle') and updates['Vehicle.Chassis.Axle.Row1.SteeringAngle'].value:
                        values["steering_angle"] = updates['Vehicle.Chassis.Axle.Row1.SteeringAngle'].value
                        # Update steering angle
                    if updates.get('Vehicle.Analytics.Anamoly') and str(updates['Vehicle.Analytics.Anamoly'].value):
                        values["anamoly"] = updates['Vehicle.Analytics.Anamoly'].value
                        if updates['Vehicle.Analytics.Anamoly'].value:
                            anomaly_count = anomaly_count + 1
    except Exception as e:
        print(f"Kuksa client error: {e}", flush=True)

# Start Kuksa client thread
kuksa_thread = Thread(target=start_kuksa_client, daemon=True)
kuksa_thread.start()

# Main loop
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read vehicle values safely
    with speed_lock:
        current_speed = values["speed"]
        throttle = values["acceleration"]
        brake = values["brake"]
        steering_angle = values["steering_angle"]
        anamoly =  values["anamoly"]

    # Draw throttle bar
    pygame.draw.rect(screen, GRAY, (50, 50, 200, 30))  # Background
    pygame.draw.rect(screen, GREEN, (50, 50, 2 * min(throttle, 100), 30))  # Foreground
    throttle_text = font.render(f"Throttle: {throttle}%", True, WHITE)
    screen.blit(throttle_text, (50, 90))

    # Draw brake bar
    pygame.draw.rect(screen, GRAY, (50, 150, 200, 30))  # Background
    pygame.draw.rect(screen, RED, (50, 150, 2 * brake, 30))  # Foreground
    brake_text = font.render(f"Brake: {brake}%", True, WHITE)
    screen.blit(brake_text, (50, 190))

    # Draw steering angle
    pygame.draw.circle(screen, GRAY, (400, 200), 100)  # Steering wheel
    draw_needle((400, 200), -math.floor(steering_angle*100), 90)  # Needle
    steering_text = font.render(f"Steering: {math.floor(steering_angle*100)}°", True, WHITE)
    screen.blit(steering_text, (350, 310))

    # Display current speed as a number
    speed_text = font.render(f"Speed: {math.floor(current_speed)} km/h", True, WHITE)
    screen.blit(speed_text, (50, 250))  # Adjust the position if needed

    speed_text = font.render(f"Anomaly: {anamoly} ", True, WHITE)
    screen.blit(speed_text, (50, 300))  # Adjust the position if needed

    speed_text = font.render(f"Anomaly count: {anomaly_count} ", True, WHITE)
    screen.blit(speed_text, (50, 350))  # Adjust the position if needed


    # Update display
    pygame.display.flip()
    clock.tick(30)

# Clean up and exit
pygame.quit()
sys.exit()
