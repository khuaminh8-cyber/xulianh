import pytesseract
from PIL import Image
import cv2
from file_utils import read_image
from config import resolve_ocr_settings


def lay_van_ban(duong_dan_anh, ngon_ngu: str = "vie") -> tuple[str, str | None]:
    try:
       
        anh = read_image(duong_dan_anh)

        if anh is None:
            raise Exception(f"Không đọc được ảnh: {duong_dan_anh}")

        anh_xam = cv2.cvtColor(anh, cv2.COLOR_BGR2GRAY)

        _, anh_nhi_phan = cv2.threshold(
            anh_xam, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        anh_pil = Image.fromarray(anh_nhi_phan)

    
        lang, tessdata_dir_override, canh_bao = resolve_ocr_settings(ngon_ngu)
        if lang is None and canh_bao and "Không tìm thấy Tesseract" in canh_bao:
            raise Exception(canh_bao)

        config = None
        if tessdata_dir_override:
            
            config = f'--tessdata-dir "{tessdata_dir_override}"'
        if lang:
            van_ban = pytesseract.image_to_string(anh_pil, lang=lang, config=config)
        else:
           
            van_ban = pytesseract.image_to_string(anh_pil, config=config)

        return van_ban, canh_bao

    except Exception as e:
        raise Exception("Lỗi OCR: " + str(e))
