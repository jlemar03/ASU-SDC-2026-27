import cv2
import numpy as np

# ============================================================
# SETTINGS
# ============================================================

# Physical size of calibration square
SQUARE_SIZE_CM = 5.0

# Distance from camera to the FRONT FACE of the square
# CHANGE THIS to your actual measured distance.
DISTANCE_CM = 20.0

# 0 is usually the built-in webcam.
# Try 1, 2, etc. if using another camera.
CAMERA_INDEX = 0

# Size of center crosshair in pixels
CROSSHAIR_SIZE = 25


# ============================================================
# GLOBAL VARIABLES
# ============================================================

points = []
frame_for_calibration = None


# ============================================================
# MOUSE CALLBACK
# ============================================================

def mouse_callback(event, x, y, flags, param):
    global points

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x, y))
            print(f"Point {len(points)}: ({x}, {y})")


# ============================================================
# OPEN CAMERA
# ============================================================

cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    print("ERROR: Could not open camera.")
    exit()


print("\n========================================")
print("CAMERA CALIBRATION")
print("========================================")

print(f"\nCalibration square: {SQUARE_SIZE_CM} x {SQUARE_SIZE_CM} cm")
print(f"Calibration distance: {DISTANCE_CM} cm")

print("\nINSTRUCTIONS:")
print("1. Place the square facing directly toward the camera.")
print("2. Measure the distance from camera to front face of square.")
print("3. Align the CENTER of the square with the red crosshair.")
print("4. Press SPACE to capture the image.")
print("5. Press Q at any time to quit.")


# ============================================================
# LIVE CAMERA
# ============================================================

while True:

    ret, frame = cap.read()

    if not ret:
        print("ERROR: Could not read camera.")
        break

    display = frame.copy()

    # --------------------------------------------------------
    # GET IMAGE CENTER
    # --------------------------------------------------------

    height, width = display.shape[:2]

    cx_display = width // 2
    cy_display = height // 2


    # --------------------------------------------------------
    # DRAW CENTER CROSSHAIR
    # --------------------------------------------------------

    # Horizontal line
    cv2.line(
        display,
        (cx_display - CROSSHAIR_SIZE, cy_display),
        (cx_display + CROSSHAIR_SIZE, cy_display),
        (0, 0, 255),
        2
    )

    # Vertical line
    cv2.line(
        display,
        (cx_display, cy_display - CROSSHAIR_SIZE),
        (cx_display, cy_display + CROSSHAIR_SIZE),
        (0, 0, 255),
        2
    )

    # Center dot
    cv2.circle(
        display,
        (cx_display, cy_display),
        5,
        (0, 0, 255),
        -1
    )


    # --------------------------------------------------------
    # DISPLAY INFORMATION
    # --------------------------------------------------------

    cv2.putText(
        display,
        "Align square center with crosshair",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        display,
        "SPACE = capture    Q = quit",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    # Display center pixel coordinates
    cv2.putText(
        display,
        f"Image center: ({cx_display}, {cy_display})",
        (20, height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


    # --------------------------------------------------------
    # SHOW CAMERA
    # --------------------------------------------------------

    cv2.imshow("Camera Calibration", display)

    key = cv2.waitKey(1) & 0xFF


    # --------------------------------------------------------
    # CAPTURE
    # --------------------------------------------------------

    if key == ord(' '):

        # IMPORTANT:
        # Save original frame WITHOUT crosshair drawn onto it.
        frame_for_calibration = frame.copy()

        print("\nImage captured.")
        break


    # --------------------------------------------------------
    # QUIT
    # --------------------------------------------------------

    elif key == ord('q'):

        cap.release()
        cv2.destroyAllWindows()
        exit()


# ============================================================
# CLOSE LIVE CAMERA
# ============================================================

cap.release()
cv2.destroyAllWindows()


if frame_for_calibration is None:
    print("No image captured.")
    exit()


# ============================================================
# SELECT FOUR CORNERS
# ============================================================

cv2.namedWindow("Select Square Corners")
cv2.setMouseCallback("Select Square Corners", mouse_callback)


print("\n========================================")
print("SELECT THE FOUR CORNERS")
print("========================================")

print("\nClick the corners in EXACTLY this order:\n")

print("       1 -------- 2")
print("       |          |")
print("       |          |")
print("       |          |")
print("       4 -------- 3")

print("\n1 = TOP LEFT")
print("2 = TOP RIGHT")
print("3 = BOTTOM RIGHT")
print("4 = BOTTOM LEFT")

print("\nControls:")
print("R = reset points")
print("ENTER = calculate calibration")
print("Q = quit")


while True:

    display = frame_for_calibration.copy()


    # --------------------------------------------------------
    # DRAW IMAGE CENTER AGAIN
    # --------------------------------------------------------

    height, width = display.shape[:2]

    cx_display = width // 2
    cy_display = height // 2

    cv2.line(
        display,
        (cx_display - CROSSHAIR_SIZE, cy_display),
        (cx_display + CROSSHAIR_SIZE, cy_display),
        (0, 255, 255),
        1
    )

    cv2.line(
        display,
        (cx_display, cy_display - CROSSHAIR_SIZE),
        (cx_display, cy_display + CROSSHAIR_SIZE),
        (0, 255, 255),
        1
    )

    cv2.circle(
        display,
        (cx_display, cy_display),
        4,
        (0, 255, 255),
        -1
    )


    # --------------------------------------------------------
    # DRAW SELECTED CORNERS
    # --------------------------------------------------------

    for i, point in enumerate(points):

        cv2.circle(
            display,
            point,
            6,
            (0, 0, 255),
            -1
        )

        cv2.putText(
            display,
            str(i + 1),
            (point[0] + 10, point[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )


    # --------------------------------------------------------
    # DRAW LINES BETWEEN SELECTED POINTS
    # --------------------------------------------------------

    if len(points) > 1:

        for i in range(len(points) - 1):

            cv2.line(
                display,
                points[i],
                points[i + 1],
                (255, 0, 0),
                2
            )


    # Close square when all four points selected
    if len(points) == 4:

        cv2.line(
            display,
            points[3],
            points[0],
            (255, 0, 0),
            2
        )


    # --------------------------------------------------------
    # DISPLAY INSTRUCTIONS
    # --------------------------------------------------------

    cv2.putText(
        display,
        f"Points selected: {len(points)}/4",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        display,
        "R = reset   ENTER = calculate   Q = quit",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )


    # --------------------------------------------------------
    # SHOW IMAGE
    # --------------------------------------------------------

    cv2.imshow("Select Square Corners", display)

    key = cv2.waitKey(1) & 0xFF


    # Reset points
    if key == ord('r'):

        points = []
        print("\nPoints reset.")


    # Enter
    elif key == 13:

        if len(points) == 4:
            break

        else:
            print("\nSelect all four corners first.")


    # Quit
    elif key == ord('q'):

        cv2.destroyAllWindows()
        exit()


cv2.destroyAllWindows()


# ============================================================
# CONVERT POINTS TO NUMPY ARRAYS
# ============================================================

TL = np.array(points[0], dtype=float)
TR = np.array(points[1], dtype=float)
BR = np.array(points[2], dtype=float)
BL = np.array(points[3], dtype=float)


# ============================================================
# MEASURE SQUARE WIDTH IN PIXELS
# ============================================================

top_width = np.linalg.norm(TR - TL)

bottom_width = np.linalg.norm(BR - BL)

width_pixels = (top_width + bottom_width) / 2.0


# ============================================================
# MEASURE SQUARE HEIGHT IN PIXELS
# ============================================================

left_height = np.linalg.norm(BL - TL)

right_height = np.linalg.norm(BR - TR)

height_pixels = (left_height + right_height) / 2.0


# ============================================================
# CALCULATE FOCAL LENGTHS
# ============================================================

# Pinhole camera equation:
#
#       pixel_size     physical_size
#       ----------  =  -------------
#           f               Z
#
#
# Therefore:
#
#       f = pixel_size * Z / physical_size


fx = (
    width_pixels
    * DISTANCE_CM
    / SQUARE_SIZE_CM
)

fy = (
    height_pixels
    * DISTANCE_CM
    / SQUARE_SIZE_CM
)


# ============================================================
# ESTIMATE PRINCIPAL POINT
# ============================================================

image_height, image_width = frame_for_calibration.shape[:2]

cx = image_width / 2.0
cy = image_height / 2.0


# ============================================================
# CREATE CAMERA INTRINSIC MATRIX
# ============================================================

K = np.array([
    [fx, 0,  cx],
    [0,  fy, cy],
    [0,  0,  1]
])


# ============================================================
# CALCULATE APPROXIMATE FIELD OF VIEW
# ============================================================

horizontal_fov = 2 * np.arctan(
    image_width / (2 * fx)
)

vertical_fov = 2 * np.arctan(
    image_height / (2 * fy)
)

horizontal_fov_deg = np.degrees(horizontal_fov)
vertical_fov_deg = np.degrees(vertical_fov)


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n")
print("========================================")
print("        CALIBRATION RESULTS")
print("========================================")


print("\nIMAGE")

print(f"Resolution = {image_width} x {image_height} pixels")

print(
    f"Assumed image center = "
    f"({cx:.2f}, {cy:.2f})"
)


print("\n----------------------------------------")
print("SQUARE MEASUREMENTS")
print("----------------------------------------")

print(f"Top width     = {top_width:.2f} px")
print(f"Bottom width  = {bottom_width:.2f} px")

print(f"Left height   = {left_height:.2f} px")
print(f"Right height  = {right_height:.2f} px")

print(f"\nAverage width  = {width_pixels:.2f} px")
print(f"Average height = {height_pixels:.2f} px")


print("\n----------------------------------------")
print("CAMERA INTRINSICS")
print("----------------------------------------")

print(f"fx = {fx:.2f} pixels")
print(f"fy = {fy:.2f} pixels")

print(f"cx = {cx:.2f} pixels")
print(f"cy = {cy:.2f} pixels")


print("\n----------------------------------------")
print("CAMERA MATRIX K")
print("----------------------------------------")

print(K)


print("\n----------------------------------------")
print("APPROXIMATE FIELD OF VIEW")
print("----------------------------------------")

print(
    f"Horizontal FOV = "
    f"{horizontal_fov_deg:.2f} degrees"
)

print(
    f"Vertical FOV   = "
    f"{vertical_fov_deg:.2f} degrees"
)


print("\n========================================")
print("DONE")
print("========================================")

print(
    "\nNOTE: cx and cy are currently assumed "
    "to be the geometric center of the image."
)

print(
    "A full checkerboard calibration is needed "
    "to accurately determine the principal point "
    "and lens distortion."
)