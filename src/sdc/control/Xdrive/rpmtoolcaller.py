from RPM_calculator_logic import motor_rpm_targets
r = 0.05  # Example wheel radius, meters

targets = motor_rpm_targets(
    vx=3.0,
    vy=4.0,
    r=r,
    gear_ratio=1.0
)

print(targets)