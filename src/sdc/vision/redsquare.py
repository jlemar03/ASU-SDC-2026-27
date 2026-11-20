import cv2
import numpy as np

# =========================================================
# CAMERA SETTINGS
# =========================================================

CAMERA_INDEX = 0

# Resolution used during calibration
CALIBRATION_WIDTH = 640
CALIBRATION_HEIGHT = 480

# Your measured camera intrinsics
FX_CALIBRATED = 434.37733465
FY_CALIBRATED = 435.33506979
CX_CALIBRATED = 320.0
CY_CALIBRATED = 240.0

# Assumed minimum physical dimensions
OBJECT_WIDTH_CM = 5.0
OBJECT_HEIGHT_CM = 5.0

# Ignore tiny red regions caused by image noise
MINIMUM_CONTOUR_AREA = 150

# =========================================================
# RED HSV RANGES
# =========================================================

# Red wraps around both ends of OpenCV's hue scale
LOWER_RED_1 = np.array([0, 100, 80])
UPPER_RED_1 = np.array([10, 255, 255])

LOWER_RED_2 = np.array([170, 100, 80])
UPPER_RED_2 = np.array([179, 255, 255])

# =========================================================
# OPEN CAMERA
# =========================================================

camera = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, CALIBRATION_WIDTH)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CALIBRATION_HEIGHT)

if not camera.isOpened():
    raise RuntimeError(
        "Could not open the camera. "
        "Try changing CAMERA_INDEX."
    )

try:
    while True:
        success, frame = camera.read()

        if not success:
            print("Could not read a camera frame.")
            break

        frame_height, frame_width = frame.shape[:2]

        # Scale the camera intrinsics if OpenCV delivers a
        # resolution different from the calibration resolution.
        scale_x = frame_width / CALIBRATION_WIDTH
        scale_y = frame_height / CALIBRATION_HEIGHT

        fx = FX_CALIBRATED * scale_x
        fy = FY_CALIBRATED * scale_y
        cx = CX_CALIBRATED * scale_x
        cy = CY_CALIBRATED * scale_y

        # =====================================================
        # CREATE RED MASK
        # =====================================================

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        red_mask_1 = cv2.inRange(
            hsv,
            LOWER_RED_1,
            UPPER_RED_1
        )

        red_mask_2 = cv2.inRange(
            hsv,
            LOWER_RED_2,
            UPPER_RED_2
        )

        red_mask = cv2.bitwise_or(
            red_mask_1,
            red_mask_2
        )

        # Remove isolated noise and fill small holes
        kernel = np.ones((5, 5), np.uint8)

        red_mask = cv2.morphologyEx(
            red_mask,
            cv2.MORPH_OPEN,
            kernel
        )

        red_mask = cv2.morphologyEx(
            red_mask,
            cv2.MORPH_CLOSE,
            kernel
        )

        # =====================================================
        # FIND RED OBJECTS
        # =====================================================

        contours, _ = cv2.findContours(
            red_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        detected_count = 0

        for contour in contours:
            contour_area = cv2.contourArea(contour)

            if contour_area < MINIMUM_CONTOUR_AREA:
                continue

            # Rotated rectangle handles a square that is rotated
            rotated_rectangle = cv2.minAreaRect(contour)

            (object_x, object_y), (
                apparent_width,
                apparent_height
            ), angle = rotated_rectangle

            if apparent_width <= 0 or apparent_height <= 0:
                continue

            # Make width the longer measured side and height
            # the shorter side. For a square they should be close.
            long_side_px = max(
                apparent_width,
                apparent_height
            )

            short_side_px = min(
                apparent_width,
                apparent_height
            )

            # Reject extremely thin red regions
            aspect_ratio = long_side_px / short_side_px

            if aspect_ratio > 2.0:
                continue

            # Estimate distance separately from width and height
            distance_from_width = (
                fx * OBJECT_WIDTH_CM / long_side_px
            )

            distance_from_height = (
                fy * OBJECT_HEIGHT_CM / short_side_px
            )

            # Average estimate works well when the square directly
            # faces the camera.
            distance_cm = (
                distance_from_width
                + distance_from_height
            ) / 2.0

            detected_count += 1

            # Convert rotated rectangle into four corner points
            box = cv2.boxPoints(rotated_rectangle)
            box = np.intp(box)

            # Draw the detected object
            cv2.drawContours(
                frame,
                [box],
                0,
                (0, 255, 0),
                3
            )

            center_x = int(object_x)
            center_y = int(object_y)

            cv2.circle(
                frame,
                (center_x, center_y),
                5,
                (255, 0, 0),
                -1
            )

            label_y = max(center_y - 25, 25)

            cv2.putText(
                frame,
                f"Distance: {distance_cm:.1f} cm",
                (max(center_x - 100, 5), label_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                (
                    f"Size: {long_side_px:.0f} x "
                    f"{short_side_px:.0f} px"
                ),
                (
                    max(center_x - 100, 5),
                    min(center_y + 35, frame_height - 10)
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        # =====================================================
        # DRAW CAMERA CENTER CROSSHAIR
        # =====================================================

        crosshair_x = int(cx)
        crosshair_y = int(cy)
        crosshair_size = 15

        cv2.line(
            frame,
            (crosshair_x - crosshair_size, crosshair_y),
            (crosshair_x + crosshair_size, crosshair_y),
            (255, 255, 0),
            2
        )

        cv2.line(
            frame,
            (crosshair_x, crosshair_y - crosshair_size),
            (crosshair_x, crosshair_y + crosshair_size),
            (255, 255, 0),
            2
        )

        cv2.circle(
            frame,
            (crosshair_x, crosshair_y),
            3,
            (255, 255, 0),
            -1
        )

        # =====================================================
        # DISPLAY INFORMATION
        # =====================================================

        cv2.putText(
            frame,
            f"Red objects: {detected_count}",
            (15, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Resolution: {frame_width} x {frame_height}",
            (15, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "Assumed target size: 4 x 4 cm",
            (15, frame_height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            "Red Object Distance Detector",
            frame
        )

        cv2.imshow(
            "Red Mask",
            red_mask
        )

        # Press Q or Escape to quit
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q") or key == 27:
            break

finally:
    camera.release()
    cv2.destroyAllWindows()