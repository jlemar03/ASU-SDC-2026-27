import numpy as np

# Every array uses this wheel order:
WHEELS = ("FL", "FR", "RL", "RR")

# Axle angles measured counterclockwise from +x.
AXLE_ANGLES = np.deg2rad([45, -45, -45, 45])


def jacobian_matrix(r):
    """Map [vx, vy] in m/s to four wheel speeds in rad/s."""
    if not np.isfinite(r) or r <= 0:
        raise ValueError("Wheel radius must be positive and finite.")

    rows = np.column_stack((
        -np.sin(AXLE_ANGLES),
         np.cos(AXLE_ANGLES)
    ))

    return rows / r


def motor_rpm_targets(vx, vy, r, gear_ratio=1.0):
    """gear_ratio = motor revolutions per wheel revolution."""
    if not np.isfinite(gear_ratio) or gear_ratio <= 0:
        raise ValueError("Gear ratio must be positive and finite.")

    velocity = np.array([vx, vy], dtype=float)

    if not np.all(np.isfinite(velocity)):
        raise ValueError("Velocity components must be finite.")

    wheel_rad_s = jacobian_matrix(r) @ velocity
    motor_rpm = wheel_rad_s * (60 / (2 * np.pi)) * gear_ratio

    return dict(zip(WHEELS, motor_rpm.tolist()))