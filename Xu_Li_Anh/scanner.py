import cv2
import numpy as np
import os
from config import STORAGE_PATH
from file_utils import read_image, write_image


def sap_xep_diem(pts):
    pts = np.array(pts, dtype="float32")
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


def tim_4_goc_chuan(anh):
    gray = cv2.cvtColor(anh, cv2.COLOR_BGR2GRAY)

    # ===== LÀM NỔI VIỀN GIẤY =====
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 30, 120)

    kernel = np.ones((5, 5), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=2)
    edges = cv2.erode(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # ===== CHỈ LẤY TỜ GIẤY =====
    c = max(contours, key=cv2.contourArea)

    # ===== TÌM ĐÚNG 4 ĐỈNH THẬT =====
    peri = cv2.arcLength(c, True)

    # ép sát cạnh nhất có thể
    approx = cv2.approxPolyDP(c, 0.005 * peri, True)

    # nếu chưa đủ 4 điểm → refine tiếp
    if len(approx) < 4:
        approx = cv2.approxPolyDP(c, 0.002 * peri, True)

    # nếu nhiều điểm → lấy convex hull rồi approx lại
    if len(approx) > 4:
        hull = cv2.convexHull(c)
        peri = cv2.arcLength(hull, True)
        approx = cv2.approxPolyDP(hull, 0.01 * peri, True)

    # fallback cuối
    if len(approx) != 4:
        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)
        return sap_xep_diem(box)

    return sap_xep_diem(approx.reshape(4, 2))


def quet_tai_lieu(duong_dan_anh):
    os.makedirs(STORAGE_PATH, exist_ok=True)

    anh = read_image(duong_dan_anh)
    if anh is None:
        raise Exception(f"Không đọc được ảnh: {duong_dan_anh}")

    anh_goc = anh.copy()

    hcn = tim_4_goc_chuan(anh_goc)

    debug = anh_goc.copy()

    if hcn is not None:
        pts = hcn.reshape(4, 1, 2).astype(np.int32)
        cv2.polylines(debug, [pts], True, (0, 255, 0), 4)
        for p in pts:
            cv2.circle(debug, tuple(p[0]), 8, (0, 0, 255), -1)

    write_image(os.path.join(STORAGE_PATH, "debug_contour.jpg"), debug)

    if hcn is None:
        write_image(os.path.join(STORAGE_PATH, "scanned.jpg"), anh_goc)
        return os.path.join(STORAGE_PATH, "scanned.jpg")

    (tl, tr, br, bl) = hcn

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = int(max(widthA, widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = int(max(heightA, heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")
    M = cv2.getPerspectiveTransform(hcn, dst)
    warped = cv2.warpPerspective(anh_goc, M, (maxWidth, maxHeight))

    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    enhanced = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        21,
        10
    )

    write_image(os.path.join(STORAGE_PATH, "enhanced.jpg"), enhanced)
    write_image(os.path.join(STORAGE_PATH, "scanned.jpg"), warped)

    return os.path.join(STORAGE_PATH, "scanned.jpg")