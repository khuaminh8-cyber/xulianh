import cv2
import os
from config import STORAGE_PATH
from file_utils import read_image, write_image


def xu_ly_anh(duong_dan_anh):
    os.makedirs(STORAGE_PATH, exist_ok=True)

    anh = read_image(duong_dan_anh)
    if anh is None:
        raise Exception(f"Không đọc được ảnh: {duong_dan_anh}")

    anh_xam = cv2.cvtColor(anh, cv2.COLOR_BGR2GRAY)

    alpha = 1.5 
    beta = 20
    anh_tang_sang = cv2.convertScaleAbs(anh_xam, alpha=alpha, beta=beta)

    lam_mo = cv2.GaussianBlur(anh_tang_sang, (5, 5), 0)

    anh_trang = cv2.adaptiveThreshold(
        lam_mo,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    duong_dan_ra = STORAGE_PATH + "enhanced.jpg"
    print(f"Lưu ảnh enhanced vào: {duong_dan_ra}")
    write_image(duong_dan_ra, anh_trang)

    return duong_dan_ra