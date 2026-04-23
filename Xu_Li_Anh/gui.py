import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2

from scanner import quet_tai_lieu
from image_utils import xu_ly_anh
from ocr_utils import lay_van_ban
from pdf_utils import anh_sang_pdf
from file_utils import read_image, write_image

duong_dan_anh = None


def tai_len_va_scan():
    global duong_dan_anh

    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    try:
        # 1. Scan tài liệu
        anh_scan = quet_tai_lieu(file_path)

        # 2. Xử lý ảnh
        anh_xu_ly = xu_ly_anh(anh_scan)

        duong_dan_anh = anh_xu_ly

        # 3. Hiển thị
        hien_thi_anh(anh_xu_ly)

        # 4. OCR
        van_ban, _canh_bao = lay_van_ban(anh_xu_ly)
        o_van_ban.delete(1.0, tk.END)
        o_van_ban.insert(tk.END, van_ban)

        # 5. Xuất PDF
        anh_sang_pdf(anh_xu_ly, "storage/output.pdf")

        messagebox.showinfo("OK", "Scan xong + đã lưu PDF!")

    except Exception as e:
        messagebox.showerror("Lỗi", str(e))


def hien_thi_anh(duong_dan):
    img = Image.open(duong_dan)
    img = img.resize((250, 300))

    img_tk = ImageTk.PhotoImage(img)

    khung_anh.config(image=img_tk)
    khung_anh.image = img_tk


def xoay_anh():
    global duong_dan_anh

    if not duong_dan_anh:
        messagebox.showwarning("Chưa có ảnh", "Hãy tải ảnh trước!")
        return

    img = read_image(duong_dan_anh)

    if img is None:
        messagebox.showerror("Lỗi", f"Không đọc được ảnh: {duong_dan_anh}")
        return

    anh_xoay = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

    write_image(duong_dan_anh, anh_xoay)
    hien_thi_anh(duong_dan_anh)


def chay_ung_dung():
    global khung_anh, o_van_ban

    cua_so = tk.Tk()
    cua_so.title("📄 Quét tài liệu")
    cua_so.geometry("500x600")

    frm_actions = tk.Frame(cua_so)
    frm_actions.pack(pady=10)

    nut_tai = tk.Button(frm_actions, text="Tải & Scan", command=tai_len_va_scan, width=18)
    nut_tai.grid(row=0, column=0, padx=6, pady=4)

    nut_xoay = tk.Button(frm_actions, text="Xoay ảnh", command=xoay_anh, width=18)
    nut_xoay.grid(row=1, column=0, padx=6, pady=4)

    khung_anh = tk.Label(cua_so)
    khung_anh.pack(pady=10)

    o_van_ban = tk.Text(cua_so, height=10, width=50)
    o_van_ban.pack(pady=10)

    cua_so.mainloop()
