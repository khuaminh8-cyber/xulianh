import cv2
import numpy as np
import os
from pathlib import Path


def read_image(path, flags=cv2.IMREAD_COLOR):
    path = str(path)
    if not path or not os.path.exists(path):
        return None

    try:
        data = np.fromfile(path, dtype=np.uint8)
        if data.size == 0:
            return None

        image = cv2.imdecode(data, flags)
        return image
    except Exception:
        return None


def write_image(path, image, params=None):
    path = str(path)
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    ext = path_obj.suffix
    if not ext:
        raise ValueError(f"Không có phần mở rộng tệp: {path}")

    result, buf = cv2.imencode(ext, image, params or [])
    if not result:
        raise IOError(f"Không thể mã hóa ảnh thành '{ext}'")

    with open(path, "wb") as f:
        f.write(buf.tobytes())
