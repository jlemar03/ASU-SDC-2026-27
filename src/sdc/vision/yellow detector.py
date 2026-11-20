import cv2
import numpy as np

# ---------------------------------------------------------
# CALIBRATION SETTINGS
# ---------------------------------------------------------

# Horizontal width of the sharpener facing the camera
KNOWN_WIDTH_CM = 5.0

# Distance between the camera lens and sharpener during calibration
CALIBRATION_DISTANCE_CM = 25.0

# Ignore very small red regions
MINIMUM_OBJECT_AREA = 500

# ---------------------------------------------------------
# RED HSV COLOR RANGES
# ---------------------------------------------------------

# Red exists at both ends of OpenCV's HSV hue range
lower_red_1 = np.array([0, 100, 80])
upper_red_1 = np.array([10, 255, 255])

lower_red_2 = np.array([170, 100, 80])
upper_red_2 = np.array([179, 255, 255])

# ---------------------------------------------------------
# CAMERA SETUP
# ---------------------------------------------------------

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    raise RuntimeError("Could not open the camera.")

focal_length_pixels = None

try:
    while True:
        success, frame = camera.read()

        if not success:
            print("Could not read a camera frame.")
            break

        frame = cv2.resize(frame, (960, 540))

        height, width = frame.shape[:2]
        one_third = width // 3

        # -------------------------------------------------
        # CREATE THE RED MASK
        # -------------------------------------------------

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        red_mask_1 = cv2.inRange(
            hsv,
            lower_red_1,
            upper_red_1
        )

        red_mask_2 = cv2.inRange(
            hsv,
            lower_red_2,
            upper_red_2
        )

        # Combine the two red ranges
        red_mask = cv2.bitwise_or(
            red_mask_1,
            red_mask_2
        )

        # Remove small dots and fill small holes
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

        # -------------------------------------------------
        # FIND RED OBJECTS
        # -------------------------------------------------

        contours, _ = cv2.findContours(
            red_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        valid_contours = []

        for contour in contours:
            area = cv2.contourArea(contour)

            if area >= MINIMUM_OBJECT_AREA:
                valid_contours.append(contour)

        left_count = 0
        center_count = 0
        right_count = 0

        calibration_pixel_width = None

        # Use the largest red object for calibration
        if valid_contours:
            largest_contour = max(
                valid_contours,
                key=cv2.contourArea
            )

            _, _, largest_width, _ = cv2.boundingRect(
                largest_contour
            )

            calibration_pixel_width = largest_width

        # -------------------------------------------------
        # PROCESS EVERY RED OBJECT
        # -------------------------------------------------

        for contour in valid_contours:
            area = cv2.contourArea(contour)

            x, y, box_width, box_height = cv2.boundingRect(
                contour
            )

            center_x = x + box_width // 2
            center_y = y + box_height // 2

            # Determine which third contains the object
            if center_x < one_third:
                region = "LEFT"
                left_count += 1

            elif center_x < 2 * one_third:
                region = "CENTER"
                center_count += 1

            else:
                region = "RIGHT"
                right_count += 1

            # Estimate distance if the system is calibrated
            if focal_length_pixels is not None:
                distance_cm = (
                    KNOWN_WIDTH_CM
                    * focal_length_pixels
                    / box_width
                )

                distance_text = f"{distance_cm:.1f} cm"

            else:
                distance_text = "Not calibrated"

            # Draw the object's bounding box
            cv2.rectangle(
                frame,
                (x, y),
                (x + box_width, y + box_height),
                (255, 0, 0),
                3
            )

            # Mark the center of the object
            cv2.circle(
                frame,
                (center_x, center_y),
                5,
                (0, 255, 0),
                -1
            )

            # Display the region and estimated distance
            cv2.putText(
                frame,
                f"RED - {region}",
                (x, max(y - 35, 25)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2
            )

            cv2.putText(
                frame,
                distance_text,
                (x, max(y - 10, 50)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 0),
                2
            )

            cv2.putText(
                frame,
                f"Width: {box_width} px",
                (x, min(y + box_height + 25, height - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 0, 0),
                2
            )

        # -------------------------------------------------
        # DRAW LEFT, CENTER, AND RIGHT REGIONS
        # -------------------------------------------------

        cv2.line(
            frame,
            (one_third, 0),
            (one_third, height),
            (0, 255, 0),
            2
        )

        cv2.line(
            frame,
            (2 * one_third, 0),
            (2 * one_third, height),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"LEFT: {left_count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"CENTER: {center_count}",
            (one_third + 20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"RIGHT: {right_count}",
            (2 * one_third + 20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 255, 0),
            2
        )

        # -------------------------------------------------
        # CALIBRATION STATUS
        # -------------------------------------------------

        if focal_length_pixels is None:
            status = (
                "Place sharpener 20 cm away, "
                "3 cm side horizontal, then press C"
            )
            status_color = (0, 0, 255)

        else:
            status = (
                f"Calibrated | Focal length: "
                f"{focal_length_pixels:.1f} px"
            )
            status_color = (255, 0, 255)

        cv2.putText(
            frame,
            status,
            (15, height - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            status_color,
            2
        )

        # -------------------------------------------------
        # DISPLAY WINDOWS
        # -------------------------------------------------

        cv2.imshow("Red Object Distance Detector", frame)
        cv2.imshow("Red Mask", red_mask)

        key = cv2.waitKey(1) & 0xFF

        # Press C to calibrate
        if key == ord("c"):
            if calibration_pixel_width is None:
                print(
                    "Calibration failed: "
                    "no sufficiently large red object detected."
                )

            else:
                focal_length_pixels = (
                    calibration_pixel_width
                    * CALIBRATION_DISTANCE_CM
                    / KNOWN_WIDTH_CM
                )

                print("\nCalibration complete")
                print(
                    f"Known width: {KNOWN_WIDTH_CM:.1f} cm"
                )
                print(
                    f"Known distance: "
                    f"{CALIBRATION_DISTANCE_CM:.1f} cm"
                )
                print(
                    f"Detected width: "
                    f"{calibration_pixel_width} pixels"
                )
                print(
                    f"Calculated focal length: "
                    f"{focal_length_pixels:.2f} pixels"
                )

        # Press Q to quit
        if key == ord("q"):
            break

finally:
    camera.release()
    cv2.destroyAllWindows()