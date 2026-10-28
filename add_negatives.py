"""Them anh NEN (khong co dien thoai) vao dataset YOLO de giam nhan nham."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import cv2
import numpy as np

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VID_EXT = {".mp4", ".avi", ".mov", ".mkv", ".webm"}


class Writer:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.count = 0
        self.n = 0

    def _split(self) -> str:
        self.n += 1
        return "valid" if self.n % 7 == 0 else "train"

    def _label(self, split: str, stem: str) -> None:
        (self.root / split / "labels" / f"{stem}.txt").write_text("", encoding="utf-8")

    def add_file(self, src: Path) -> None:
        split = self._split()
        stem = f"neg_{src.stem}"
        dst = self.root / split / "images" / f"{stem}{src.suffix.lower()}"
        if dst.exists():
            return
        shutil.copy2(src, dst)
        self._label(split, stem)
        self.count += 1

    def add_frame(self, frame: np.ndarray, stem: str) -> None:
        split = self._split()
        dst = self.root / split / "images" / f"{stem}.jpg"
        if dst.exists():
            return
        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
        if not ok:
            return
        buf.tofile(str(dst))
        self._label(split, stem)
        self.count += 1


def from_video(w: Writer, path: Path, every: float, max_frames: int) -> None:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        print(f"Khong mo duoc video: {path}")
        return
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    step = max(1, int(fps * every))
    idx = taken = 0
    while taken < max_frames:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            w.add_frame(frame, f"neg_{path.stem[:20]}_{idx:06d}")
            taken += 1
        idx += 1
    cap.release()
    print(f"{path.name}: lay {taken} khung")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("sources", type=Path, nargs="+")
    ap.add_argument("--every", type=float, default=3.0)
    ap.add_argument("--max", type=int, default=300)
    a = ap.parse_args()

    for split in ("train", "valid"):
        (a.root / split / "images").mkdir(parents=True, exist_ok=True)
        (a.root / split / "labels").mkdir(parents=True, exist_ok=True)

    w = Writer(a.root)
    for src in a.sources:
        if not src.exists():
            print(f"Bo qua (khong ton tai): {src}")
        elif src.is_dir():
            for f in sorted(src.rglob("*")):
                if f.suffix.lower() in IMG_EXT:
                    w.add_file(f)
                elif f.suffix.lower() in VID_EXT:
                    from_video(w, f, a.every, a.max)
        elif src.suffix.lower() in VID_EXT:
            from_video(w, src, a.every, a.max)
        elif src.suffix.lower() in IMG_EXT:
            w.add_file(src)
    print(f"Da them {w.count} anh nen vao {a.root}")


if __name__ == "__main__":
    main()