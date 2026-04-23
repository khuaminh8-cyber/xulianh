from fpdf import FPDF
from PIL import Image


def anh_sang_pdf(duong_dan_anh, duong_dan_pdf):
    try:
        pdf = FPDF(unit='mm', format='A4')
        pdf.add_page()

        img = Image.open(duong_dan_anh)
        w_img, h_img = img.size
        w_pdf = 210
        h_pdf = 297
        ti_le = min(w_pdf / w_img, h_pdf / h_img)

        w_moi = w_img * ti_le
        h_moi = h_img * ti_le
        x = (w_pdf - w_moi) / 2
        y = (h_pdf - h_moi) / 2

        pdf.image(duong_dan_anh, x=x, y=y, w=w_moi, h=h_moi)
        pdf.output(duong_dan_pdf)

    except Exception as e:
        raise Exception("Lỗi tạo PDF: " + str(e))