import cv2
import numpy as np

# =========================================================
# SETTINGS
# =========================================================

CAMERA_INDEX = 0
SQUARE_SIDE_CM = 5.0

MINIMUM_CONTOUR_AREA = 300

CALIBRATION_WIDTH = 640
CALIBRATION_HEIGHT = 480

FX_CALIBRATED = 434.37733465
FY_CALIBRATED = 435.33506979
CX_CALIBRATED = 320.0
CY_CALIBRATED = 240.0

DISTORTION = np.zeros((5, 1), dtype=np.float64)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def order_corners(points):
    """
    Order points:
    top-left, top-right, bottom-right, bottom-left.
    """

    points = np.asarray(points, dtype=np.float32)

    ordered = np.zeros((4, 2), dtype=np.float32)

    coordinate_sum = points.sum(axis=1)
    coordinate_difference = np.diff(
        points,
        axis=1
    ).reshape(-1)

    ordered[0] = points[np.argmin(coordinate_sum)]
    ordered[2] = points[np.argmax(coordinate_sum)]
    ordered[1] = points[np.argmin(coordinate_difference)]
    ordered[3] = points[np.argmax(coordinate_difference)]

    return ordered


def corner_angle_cosine(
    point_before,
    corner,
    point_after
):
    vector_1 = point_before - corner
    vector_2 = point_after - corner

    denominator = (
        np.linalg.norm(vector_1)
        * np.linalg.norm(vector_2)
    )

    if denominator == 0:
        return 1.0

    return abs(
        np.dot(vector_1, vector_2)
        / denominator
    )


def looks_like_square(points):
    """
    Strict test used for complete four-sided contours.
    """

    points = order_corners(points)

    top_left = points[0]
    top_right = points[1]
    bottom_right = points[2]
    bottom_left = points[3]

    side_lengths = [
        np.linalg.norm(top_right - top_left),
        np.linalg.norm(bottom_right - top_right),
        np.linalg.norm(bottom_left - bottom_right),
        np.linalg.norm(top_left - bottom_left)
    ]

    shortest_side = min(side_lengths)
    longest_side = max(side_lengths)

    if shortest_side <= 0:
        return False

    if longest_side / shortest_side > 1.5:
        return False

    angle_cosines = [
        corner_angle_cosine(
            bottom_left,
            top_left,
            top_right
        ),
        corner_angle_cosine(
            top_left,
            top_right,
            bottom_right
        ),
        corner_angle_cosine(
            top_right,
            bottom_right,
            bottom_left
        ),
        corner_angle_cosine(
            bottom_right,
            bottom_left,
            top_left
        )
    ]

    if max(angle_cosines) > 0.45:
        return False

    return True


def calculate_edge_coverage(
    box_points,
    nearby_edges,
    samples_per_side=50
):
    """
    Determine how much of the predicted square perimeter
    is supported by detected edges.

    This allows a square with part of one edge missing.
    """

    box_points = order_corners(box_points)

    side_coverages = []

    for side_index in range(4):
        start = box_points[side_index]
        end = box_points[(side_index + 1) % 4]

        detected_samples = 0
        valid_samples = 0

        for sample_index in range(samples_per_side):
            fraction = (
                sample_index
                / (samples_per_side - 1)
            )

            point = (
                start
                + fraction * (end - start)
            )

            x = int(round(point[0]))
            y = int(round(point[1]))

            if (
                0 <= x < nearby_edges.shape[1]
                and 0 <= y < nearby_edges.shape[0]
            ):
                valid_samples += 1

                if nearby_edges[y, x] > 0:
                    detected_samples += 1

        if valid_samples == 0:
            side_coverages.append(0.0)
        else:
            side_coverages.append(
                detected_samples / valid_samples
            )

    average_coverage = float(
        np.mean(side_coverages)
    )

    reasonably_visible_sides = sum(
        coverage >= 0.45
        for coverage in side_coverages
    )

    return (
        average_coverage,
        reasonably_visible_sides,
        side_coverages
    )


def incomplete_square_candidate(
    contour,
    nearby_edges
):
    """
    Fit a square around an incomplete contour and check
    whether detected edges support most of its perimeter.
    """

    rectangle = cv2.minAreaRect(contour)

    rectangle_width = rectangle[1][0]
    rectangle_height = rectangle[1][1]

    if rectangle_width <= 0 or rectangle_height <= 0:
        return None

    longest_side = max(
        rectangle_width,
        rectangle_height
    )

    shortest_side = min(
        rectangle_width,
        rectangle_height
    )

    # Reject strongly rectangular shapes
    if longest_side / shortest_side > 1.5:
        return None

    box_points = cv2.boxPoints(
        rectangle
    ).astype(np.float32)

    (
        average_coverage,
        visible_sides,
        side_coverages
    ) = calculate_edge_coverage(
        box_points,
        nearby_edges
    )

    # Accept three mostly visible sides, allowing part
    # of the fourth side to be absent.
    if visible_sides < 3:
        return None

    if average_coverage < 0.50:
        return None

    return order_corners(box_points)


def is_duplicate(
    center,
    accepted_centers,
    threshold=20
):
    for accepted_center in accepted_centers:
        if np.linalg.norm(
            center - accepted_center
        ) < threshold:
            return True

    return False


# =========================================================
# CAMERA SETUP
# =========================================================

camera = cv2.VideoCapture(
    CAMERA_INDEX,
    cv2.CAP_DSHOW
)

camera.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    CALIBRATION_WIDTH
)

camera.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    CALIBRATION_HEIGHT
)

if not camera.isOpened():
    raise RuntimeError(
        "Could not open the camera. "
        "Try another CAMERA_INDEX."
    )


# =========================================================
# PHYSICAL SQUARE COORDINATES
# =========================================================

half_side = SQUARE_SIDE_CM / 2.0

object_points = np.array(
    [
        [-half_side,  half_side, 0.0],
        [ half_side,  half_side, 0.0],
        [ half_side, -half_side, 0.0],
        [-half_side, -half_side, 0.0]
    ],
    dtype=np.float32
)


# =========================================================
# MAIN LOOP
# =========================================================

try:
    while True:
        success, frame = camera.read()

        if not success:
            print("Could not read the camera.")
            break

        frame_height, frame_width = frame.shape[:2]

        scale_x = (
            frame_width / CALIBRATION_WIDTH
        )

        scale_y = (
            frame_height / CALIBRATION_HEIGHT
        )

        fx = FX_CALIBRATED * scale_x
        fy = FY_CALIBRATED * scale_y
        cx = CX_CALIBRATED * scale_x
        cy = CY_CALIBRATED * scale_y

        camera_matrix = np.array(
            [
                [fx, 0.0, cx],
                [0.0, fy, cy],
                [0.0, 0.0, 1.0]
            ],
            dtype=np.float64
        )

        # =================================================
        # EDGE DETECTION
        # =================================================

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        blurred = cv2.GaussianBlur(
            gray,
            (5, 5),
            0
        )

        edges = cv2.Canny(
            blurred,
            30,
            100
        )

        # Light closing only. Heavy dilation changes the
        # apparent square dimensions and hurts accuracy.
        edges_closed = cv2.morphologyEx(
            edges,
            cv2.MORPH_CLOSE,
            np.ones((3, 3), np.uint8),
            iterations=1
        )

        # Used only to check whether an edge is located
        # near a predicted side.
        nearby_edges = cv2.dilate(
            edges,
            np.ones((7, 7), np.uint8),
            iterations=1
        )

        contours, _ = cv2.findContours(
            edges_closed,
            cv2.RETR_LIST,
            cv2.CHAIN_APPROX_SIMPLE
        )

        contours = sorted(
            contours,
            key=cv2.contourArea,
            reverse=True
        )

        square_count = 0
        accepted_centers = []

        # =================================================
        # SQUARE DETECTION
        # =================================================

        for contour in contours:
            contour_area = cv2.contourArea(
                contour
            )

            if contour_area < MINIMUM_CONTOUR_AREA:
                continue

            perimeter = cv2.arcLength(
                contour,
                True
            )

            approximation = cv2.approxPolyDP(
                contour,
                0.02 * perimeter,
                True
            )

            image_points = None
            detection_type = None

            # ---------------------------------------------
            # Method 1: original complete-square algorithm
            # ---------------------------------------------

            if (
                len(approximation) == 4
                and cv2.isContourConvex(approximation)
            ):
                candidate_points = (
                    approximation
                    .reshape(4, 2)
                    .astype(np.float32)
                )

                if looks_like_square(
                    candidate_points
                ):
                    image_points = order_corners(
                        candidate_points
                    )

                    detection_type = "COMPLETE"

            # ---------------------------------------------
            # Method 2: incomplete-square fallback
            # ---------------------------------------------

            if image_points is None:
                image_points = incomplete_square_candidate(
                    contour,
                    nearby_edges
                )

                if image_points is not None:
                    detection_type = "INCOMPLETE"

            if image_points is None:
                continue

            object_center = np.mean(
                image_points,
                axis=0
            )

            if is_duplicate(
                object_center,
                accepted_centers
            ):
                continue

            # =================================================
            # ORIGINAL DISTANCE / POSE ALGORITHM
            # =================================================

            pose_found, rotation_vector, translation_vector = (
                cv2.solvePnP(
                    object_points,
                    image_points,
                    camera_matrix,
                    DISTORTION,
                    flags=cv2.SOLVEPNP_IPPE_SQUARE
                )
            )

            if not pose_found:
                continue

            x_cm = float(
                translation_vector[0, 0]
            )

            y_cm = float(
                translation_vector[1, 0]
            )

            z_cm = float(
                translation_vector[2, 0]
            )

            if z_cm <= 0:
                continue

            range_cm = float(
                np.linalg.norm(
                    translation_vector
                )
            )

            accepted_centers.append(
                object_center
            )

            square_count += 1

            # =================================================
            # DRAW RESULTS
            # =================================================

            display_points = image_points.astype(
                np.int32
            )

            if detection_type == "COMPLETE":
                box_color = (0, 255, 0)
            else:
                box_color = (0, 165, 255)

            cv2.polylines(
                frame,
                [display_points],
                True,
                box_color,
                3
            )

            center_x = int(
                object_center[0]
            )

            center_y = int(
                object_center[1]
            )

            cv2.circle(
                frame,
                (center_x, center_y),
                5,
                (0, 0, 255),
                -1
            )

            text_x = max(
                center_x - 110,
                5
            )

            text_y = max(
                center_y - 70,
                25
            )

            cv2.putText(
                frame,
                detection_type,
                (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                box_color,
                2
            )

            cv2.putText(
                frame,
                f"Range: {range_cm:.1f} cm",
                (text_x, text_y + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                box_color,
                2
            )

            cv2.putText(
                frame,
                f"Forward: {z_cm:.1f} cm",
                (text_x, text_y + 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                box_color,
                2
            )

            cv2.putText(
                frame,
                (
                    f"X: {x_cm:.1f}, "
                    f"Y: {y_cm:.1f} cm"
                ),
                (text_x, text_y + 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                box_color,
                2
            )

        # =================================================
        # CAMERA CROSSHAIR
        # =================================================

        crosshair_x = int(cx)
        crosshair_y = int(cy)

        cv2.line(
            frame,
            (crosshair_x - 15, crosshair_y),
            (crosshair_x + 15, crosshair_y),
            (255, 255, 0),
            2
        )

        cv2.line(
            frame,
            (crosshair_x, crosshair_y - 15),
            (crosshair_x, crosshair_y + 15),
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

        cv2.putText(
            frame,
            f"Squares: {square_count}",
            (15, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            (
                f"Target size: "
                f"{SQUARE_SIDE_CM:.1f} x "
                f"{SQUARE_SIDE_CM:.1f} cm"
            ),
            (15, frame_height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            "Square Distance Detector",
            frame
        )

        cv2.imshow(
            "Detected Edges",
            edges
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q") or key == 27:
            break

finally:
    camera.release()
    cv2.destroyAllWindows()