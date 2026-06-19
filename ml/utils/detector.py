"""
YOLO v8 parking violation detector wrapper.
Falls back to a mock detector if no model file is present (for dev).
"""
import os
import logging
import numpy as np

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.65"))

# Class names — must match your YOLO training labels
CLASS_NAMES = ["legally_parked", "illegally_parked", "no_vehicle"]
VIOLATION_CLASSES = {"illegally_parked"}


class ParkingDetector:
    def __init__(self, model_path: str):
        self.model = None
        self.mock_mode = False

        if not os.path.exists(model_path):
            logger.warning(
                "Model file not found at %s — running in MOCK mode. "
                "Train the model and place best.pt at that path.",
                model_path,
            )
            self.mock_mode = True
            return

        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            logger.info("YOLO model loaded from %s", model_path)
        except Exception as e:
            logger.error("Failed to load YOLO model: %s — mock mode", e)
            self.mock_mode = True

    def detect(self, img_array: np.ndarray) -> list[dict]:
        """
        Run inference on a frame.
        Returns list of violation dicts (empty list = no violations).
        """
        if self.mock_mode:
            return self._mock_detect()

        results = self.model.predict(
            img_array,
            conf=CONFIDENCE_THRESHOLD,
            verbose=False,
        )

        violations = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                cls_name = CLASS_NAMES[cls_id] if cls_id < len(CLASS_NAMES) else "unknown"
                if cls_name not in VIOLATION_CLASSES:
                    continue
                x1, y1, x2, y2 = box.xyxyn[0].tolist()   # normalised
                violations.append({
                    "detected":     True,
                    "confidence":   round(float(box.conf[0]), 3),
                    "bbox":         [round(x1,3), round(y1,3), round(x2,3), round(y2,3)],
                    "vehicle_type": "unknown",
                })
        return violations

    def _mock_detect(self) -> list[dict]:
        """Returns empty list — no violations in mock mode."""
        return []
