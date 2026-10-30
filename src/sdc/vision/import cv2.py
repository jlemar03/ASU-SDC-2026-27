import cv2

# Open the default camera
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    raise RuntimeError("Could not open the camera.")

try:
    while True:
        success, frame = camera.read()

        if not success:
            print("Could not read a camera frame.")
            break

        # Resize the camera image
        frame = cv2.resize(frame, (960, 540))

        height, width = frame.shape[:2]
        one_third = width // 3

        # -----------------------------------------------------
        # PROCESS THE IMAGE
        # -----------------------------------------------------

        # Convert the original frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Blur the image to reduce small noisy edges
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Detect edges
        edges = cv2.Canny(blurred, 50, 150)

        # Split the edge image into three regions
        left_edges = edges[:, 0:one_third]
        center_edges = edges[:, one_third:2 * one_third]
        right_edges = edges[:, 2 * one_third:width]

        # Calculate the percentage of edge pixels in each region
        left_amount = (
            100 * cv2.countNonZero(left_edges) / left_edges.size
        )

        center_amount = (
            100 * cv2.countNonZero(center_edges) / center_edges.size
        )

        right_amount = (
            100 * cv2.countNonZero(right_edges) / right_edges.size
        )

        amounts = {
            "LEFT": left_amount,
            "CENTER": center_amount,
            "RIGHT": right_amount
        }

        # Find the region with the fewest edges
        clearest_direction = min(amounts, key=amounts.get)

        # -----------------------------------------------------
        # DRAW RESULTS ON THE CAMERA FRAME
        # -----------------------------------------------------

        # Divide the camera image into three regions
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

        # Region names
        cv2.putText(
            frame,
            "LEFT",
            (40, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "CENTER",
            (one_third + 40, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "RIGHT",
            (2 * one_third + 40, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        # Edge percentages
        cv2.putText(
            frame,
            f"{left_amount:.1f}%",
            (40, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"{center_amount:.1f}%",
            (one_third + 40, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"{right_amount:.1f}%",
            (2 * one_third + 40, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        # Suggested direction
        cv2.putText(
            frame,
            f"Clearest direction: {clearest_direction}",
            (20, height - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 0, 255),
            2
        )

        # Print the measurements in the terminal
        print(
            f"Left: {left_amount:.2f}% | "
            f"Center: {center_amount:.2f}% | "
            f"Right: {right_amount:.2f}% | "
            f"Clearest: {clearest_direction}"
        )

        # Show the normal camera and detected edges
        cv2.imshow("Camera Regions", frame)
        cv2.imshow("Detected Edges", edges)

        # Press Q to close
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    camera.release()
    cv2.destroyAllWindows()