from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path.cwd()

EDITS: dict[str, list[tuple[str, str]]] = {
    "backend/app/core/config.py": [
        (
            "    face_model_path: str | None = None\n    device: str = \"auto\"\n",
            "    face_model_path: str | None = None\n"
            "    # Model YOLO riêng chỉ để tìm điện thoại (tùy chọn). Khi đặt, model chính\n"
            "    # chỉ còn dùng để tìm người.\n"
            "    phone_model_path: str | None = None\n"
            "    phone_model_class_id: int = 0\n"
            "    device: str = \"auto\"\n",
        ),
    ],
    "ml/models/detector.py": [
        (
            "        face_model_path: str | None = None,\n    ) -> None:\n        from ultralytics import YOLO",
            "        face_model_path: str | None = None,\n"
            "        phone_model_path: str | None = None,\n"
            "        phone_model_class_id: int = 0,\n"
            "    ) -> None:\n        from ultralytics import YOLO",
        ),
        (
            "        self.face_model = YOLO(face_model_path) if face_model_path else None\n",
            "        self.face_model = YOLO(face_model_path) if face_model_path else None\n"
            "        self.phone_model = YOLO(phone_model_path) if phone_model_path else None\n"
            "        self.phone_model_class_id = phone_model_class_id\n",
        ),
        (
            "        results = self.model.predict(\n",
            "        # Có model điện thoại riêng thì model chính chỉ tìm người.\n"
            "        main_classes = (\n"
            "            [self.person_class_id]\n"
            "            if self.phone_model is not None\n"
            "            else [self.person_class_id, self.phone_class_id]\n"
            "        )\n"
            "        results = self.model.predict(\n",
        ),
        (
            "            classes=[self.person_class_id, self.phone_class_id],\n",
            "            classes=main_classes,\n",
        ),
        (
            "        if self.face_model is not None:\n            face_results",
            "        if self.phone_model is not None:\n"
            "            phone_results = self.phone_model.predict(\n"
            "                frame_bgr,\n"
            "                conf=self.confidence,\n"
            "                iou=self.iou,\n"
            "                device=self.device,\n"
            "                max_det=self.max_detections,\n"
            "                classes=[self.phone_model_class_id],\n"
            "                verbose=False,\n"
            "            )[0]\n"
            "            phone_boxes = phone_results.boxes\n"
            "            if phone_boxes is not None:\n"
            "                for xyxy, conf in zip(\n"
            "                    phone_boxes.xyxy.cpu().numpy(), phone_boxes.conf.cpu().numpy()\n"
            "                ):\n"
            "                    output.phones.append(\n"
            "                        Detection(\n"
            "                            bbox=tuple(float(v) for v in xyxy),\n"
            "                            confidence=float(conf),\n"
            "                            class_id=self.phone_class_id,\n"
            "                        )\n"
            "                    )\n\n"
            "        if self.face_model is not None:\n            face_results",
        ),
    ],
    "ml/pipeline.py": [
        (
            "            face_model_path=d.face_model_path,\n        )\n    else:",
            "            face_model_path=d.face_model_path,\n"
            "            phone_model_path=d.phone_model_path,\n"
            "            phone_model_class_id=d.phone_model_class_id,\n"
            "        )\n    else:",
        ),
    ],
    "config.yaml": [
        ('  backend: "mediapipe"\n', '  backend: "yolo"\n'),
        (
            "  face_model_path: null\n",
            "  face_model_path: null\n"
            '  phone_model_path: "yolo_weights/phone_best.pt"   # model điện thoại tự huấn luyện\n'
            "  phone_model_class_id: 0\n",
        ),
    ],
}


def main() -> None:
    new_text: dict[str, str] = {}
    for rel, edits in EDITS.items():
        path = ROOT / rel
        if not path.exists():
            raise SystemExit(f"Không thấy {rel}. Hãy chạy script trong thư mục gốc project.")
        text = path.read_text(encoding="utf-8")
        if "phone_model_path" in text:
            raise SystemExit(f"{rel} đã được vá rồi. Dừng lại.")
        for old, new in edits:
            if text.count(old) != 1:
                raise SystemExit(
                    f"Không khớp đoạn cần sửa trong {rel} (tìm thấy {text.count(old)} lần):\n{old}"
                )
            text = text.replace(old, new)
        new_text[rel] = text

    for rel, text in new_text.items():
        path = ROOT / rel
        shutil.copy2(path, path.with_name(path.name + ".bak"))
        path.write_text(text, encoding="utf-8")
        print(f"Đã vá {rel}")
    print("\nXong. Nhớ copy best.pt vào yolo_weights/phone_best.pt")


if __name__ == "__main__":
    sys.exit(main())