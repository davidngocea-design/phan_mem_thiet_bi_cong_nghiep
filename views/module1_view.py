"""
File: views/module1_view.py
Chức năng: Giao diện MODULE 1 - TÍNH TOÁN PHỤ TẢI CÔNG NGHIỆP (Gồm đúng 2 Tab):
  - Tab 1 (Thành viên 1): Mạch 1 Pha & Đề xuất Tụ Bù cosφ
  - Tab 2 (Thành viên 2): Động Cơ Không Đồng Bộ 3 Pha & Đề xuất Khởi Động Từ
"""

import tkinter as tk
from tkinter import ttk, messagebox
from utils.validation import validate_float, validate_int, validate_ratio
from utils.history import save_calculation_record
from utils.exporter import format_record_as_text
from modules.module1_phu_tai import (
    tinh_phu_tai_1_pha_va_tu_bu,
    tinh_dong_co_3_pha_va_khoi_dong_tu
)


class Module1PhuTaiView(ttk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app = app_controller
        self.last_motor_p_kw = 11.0
        self.last_motor_u_v = 380.0
        self.last_motor_cos = 0.85
        self.tao_giao_dien()

    def tao_giao_dien(self):
        lbl_title = tk.Label(
            self,
            text="MODULE 1: TÍNH TOÁN PHỤ TẢI & ĐỀ XUẤT THIẾT BỊ ĐIỀU KHIỂN - BÙ CÔNG SUẤT",
            font=("Arial", 12, "bold"), fg="#0f172a"
        )
        lbl_title.pack(anchor="w", padx=12, pady=(10, 6))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="x", padx=12, pady=4)

        self.tab1 = ttk.Frame(self.notebook, padding=12)
        self.tab2 = ttk.Frame(self.notebook, padding=12)

        self.notebook.add(self.tab1, text=" Tab 1 (TV1): Phụ Tải 1 Pha & Đề Xuất Tụ Bù cosφ ")
        self.notebook.add(self.tab2, text=" Tab 2 (TV2): Động Cơ KĐB 3 Pha & Đề Xuất Khởi Động Từ ")

        self.dung_tab_1()
        self.dung_tab_2()

        frame_kq = ttk.LabelFrame(self, text=" Báo Cáo Kết Quả Tính Toán & Đề Xuất Thiết Bị Công Nghiệp ", padding=8)
        frame_kq.pack(fill="both", expand=True, padx=12, pady=8)

        self.txt_result = tk.Text(frame_kq, height=12, font=("Consolas", 10), bg="#f8fafc")
        self.txt_result.pack(fill="both", expand=True)

    def dung_tab_1(self):
        ttk.Label(self.tab1, text="Công suất tác dụng P (kW):").grid(row=0, column=0, sticky="w", pady=6)
        self.ent_p1 = ttk.Entry(self.tab1, width=18)
        self.ent_p1.insert(0, "50")
        self.ent_p1.grid(row=0, column=1, padx=8, pady=6)

        ttk.Label(self.tab1, text="Điện áp lưới U (V):").grid(row=0, column=2, sticky="w", pady=6)
        self.ent_u1 = ttk.Entry(self.tab1, width=18)
        self.ent_u1.insert(0, "220")
        self.ent_u1.grid(row=0, column=3, padx=8, pady=6)

        ttk.Label(self.tab1, text="Hệ số cosφ1 (Trước khi bù):").grid(row=1, column=0, sticky="w", pady=6)
        self.ent_cos1 = ttk.Entry(self.tab1, width=18)
        self.ent_cos1.insert(0, "0.70")
        self.ent_cos1.grid(row=1, column=1, padx=8, pady=6)

        ttk.Label(self.tab1, text="Hệ số cosφ2 (Mục tiêu sau bù):").grid(row=1, column=2, sticky="w", pady=6)
        self.ent_cos2 = ttk.Entry(self.tab1, width=18)
        self.ent_cos2.insert(0, "0.95")
        self.ent_cos2.grid(row=1, column=3, padx=8, pady=6)

        btn_calc1 = tk.Button(
            self.tab1, text="Tính Dung Lượng Bù & Đề Xuất Tụ Bù + CB",
            bg="#0284c7", fg="white", font=("Arial", 10, "bold"),
            padx=14, pady=5, command=self.xu_ly_tab_1
        )
        btn_calc1.grid(row=2, column=0, columnspan=4, pady=10)

    def dung_tab_2(self):
        ttk.Label(self.tab2, text="Công suất động cơ P (kW):").grid(row=0, column=0, sticky="w", pady=4)
        self.ent_p2 = ttk.Entry(self.tab2, width=16)
        self.ent_p2.insert(0, "11")
        self.ent_p2.grid(row=0, column=1, padx=8, pady=4)

        ttk.Label(self.tab2, text="Điện áp dây Ud (V):").grid(row=0, column=2, sticky="w", pady=4)
        self.ent_u2 = ttk.Entry(self.tab2, width=16)
        self.ent_u2.insert(0, "380")
        self.ent_u2.grid(row=0, column=3, padx=8, pady=4)

        ttk.Label(self.tab2, text="Tần số lưới f (Hz):").grid(row=1, column=0, sticky="w", pady=4)
        self.ent_f2 = ttk.Entry(self.tab2, width=16)
        self.ent_f2.insert(0, "50")
        self.ent_f2.grid(row=1, column=1, padx=8, pady=4)

        ttk.Label(self.tab2, text="Số đôi cực từ p:").grid(row=1, column=2, sticky="w", pady=4)
        self.ent_poles = ttk.Entry(self.tab2, width=16)
        self.ent_poles.insert(0, "2")
        self.ent_poles.grid(row=1, column=3, padx=8, pady=4)

        ttk.Label(self.tab2, text="Tốc độ thực tế n (vòng/phút):").grid(row=2, column=0, sticky="w", pady=4)
        self.ent_n2 = ttk.Entry(self.tab2, width=16)
        self.ent_n2.insert(0, "1450")
        self.ent_n2.grid(row=2, column=1, padx=8, pady=4)

        ttk.Label(self.tab2, text="Hệ số công suất cosφ:").grid(row=2, column=2, sticky="w", pady=4)
        self.ent_cos_m = ttk.Entry(self.tab2, width=16)
        self.ent_cos_m.insert(0, "0.85")
        self.ent_cos_m.grid(row=2, column=3, padx=8, pady=4)

        ttk.Label(self.tab2, text="Hiệu suất động cơ η:").grid(row=3, column=0, sticky="w", pady=4)
        self.ent_eff = ttk.Entry(self.tab2, width=16)
        self.ent_eff.insert(0, "0.89")
        self.ent_eff.grid(row=3, column=1, padx=8, pady=4)

        frame_btn = ttk.Frame(self.tab2)
        frame_btn.grid(row=4, column=0, columnspan=4, pady=8)

        btn_calc2 = tk.Button(
            frame_btn, text="Tính Động Cơ & Đề Xuất Contactor + Rơ Le Nhiệt",
            bg="#0284c7", fg="white", font=("Arial", 10, "bold"),
            padx=12, pady=5, command=self.xu_ly_tab_2
        )
        btn_calc2.pack(side="left", padx=6)

        btn_link = tk.Button(
            frame_btn, text="Chuyển sang Module 2 (Chọn Cáp Cho Động Cơ Này)",
            bg="#059669", fg="white", font=("Arial", 10, "bold"),
            padx=12, pady=5, command=self.chuyen_sang_chon_cap
        )
        btn_link.pack(side="left", padx=6)

    def hien_thi_ket_qua(self, record):
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert(tk.END, format_record_as_text(record))
        self.app.cap_nhat_lich_su(record)

    def xu_ly_tab_1(self):
        try:
            p_kw = validate_float(self.ent_p1.get(), "Công suất P (kW)")
            u_v = validate_float(self.ent_u1.get(), "Điện áp U (V)")
            cos1 = validate_ratio(self.ent_cos1.get(), "Hệ số cosφ1 ban đầu")
            cos2 = validate_ratio(self.ent_cos2.get(), "Hệ số cosφ2 mục tiêu")

            results, equipment = tinh_phu_tai_1_pha_va_tu_bu(p_kw, u_v, cos1, cos2, 50.0)
            inputs = {
                "Công suất tác dụng P": f"{p_kw} kW",
                "Điện áp lưới U": f"{u_v} V (50 Hz)",
                "Hệ số cosφ trước -> sau bù": f"{cos1} -> {cos2}"
            }
            record = save_calculation_record("Module 1 (Tab 1) - Bù công suất phản kháng", inputs, results, equipment)
            self.hien_thi_ket_qua(record)
        except ValueError as e:
            messagebox.showerror("Lỗi nhập liệu / Logic", str(e))

    def xu_ly_tab_2(self):
        try:
            p_kw = validate_float(self.ent_p2.get(), "Công suất động cơ P (kW)")
            u_d = validate_float(self.ent_u2.get(), "Điện áp dây Ud (V)")
            f_hz = validate_float(self.ent_f2.get(), "Tần số f (Hz)")
            poles = validate_int(self.ent_poles.get(), "Số đôi cực từ p")
            n_real = validate_float(self.ent_n2.get(), "Tốc độ thực tế n (vòng/phút)")
            cos_phi = validate_ratio(self.ent_cos_m.get(), "Hệ số công suất cosφ")
            eff = validate_ratio(self.ent_eff.get(), "Hiệu suất động cơ η")

            results, equipment, p_dien_kw = tinh_dong_co_3_pha_va_khoi_dong_tu(
                p_kw, u_d, f_hz, poles, n_real, cos_phi, eff
            )

            self.last_motor_p_kw = round(p_dien_kw, 2)
            self.last_motor_u_v = u_d
            self.last_motor_cos = cos_phi

            inputs = {
                "Công suất định mức P": f"{p_kw} kW (Ud = {u_d} V, f = {f_hz} Hz)",
                "Số đôi cực & Tốc độ quay": f"p = {poles} đôi cực, n = {n_real} vòng/phút",
                "Hệ số cosφ & Hiệu suất η": f"cosφ = {cos_phi}, η = {eff}"
            }
            record = save_calculation_record("Module 1 (Tab 2) - Động cơ KĐB 3 pha", inputs, results, equipment)
            self.hien_thi_ket_qua(record)
        except ValueError as e:
            messagebox.showerror("Lỗi nhập liệu / Vật lý", str(e))

    def chuyen_sang_chon_cap(self):
        self.app.chuyen_du_lieu_sang_module_2(
            self.last_motor_p_kw, self.last_motor_u_v, self.last_motor_cos
        )
