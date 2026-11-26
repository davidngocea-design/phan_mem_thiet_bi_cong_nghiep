"""
File: views/module2_view.py
Chức năng: Giao diện MODULE 2 - TRUYỀN TẢI & BẢO VỆ CÔNG NGHIỆP (Gồm đúng 2 Tab):
  - Chọn Cáp Điện & Vòng Lặp Kiểm Tra Sụt Áp (ΔU% <= 5%)
  - Tính Ngắn Mạch & Đề Xuất Thiết Bị Đóng Cắt (MCB / MCCB)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from utils.validation import validate_float, validate_ratio
from utils.history import save_calculation_record
from utils.exporter import format_record_as_text
from modules.module2_truyen_tai_bao_ve import (
    tinh_chon_cap_va_sut_ap,
    tinh_ngan_mach_va_chon_cb
)


class Module2TruyenTaiView(ttk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app = app_controller
        self.tao_giao_dien()

    def tao_giao_dien(self):
        lbl_title = tk.Label(
            self,
            text="TÍNH TOÁN TRUYỀN TẢI & ĐỀ XUẤT CÁP ĐIỆN - THIẾT BỊ BẢO VỆ",
            font=("Arial", 12, "bold"), fg="#0f172a"
        )
        lbl_title.pack(anchor="w", padx=12, pady=(10, 6))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="x", padx=12, pady=4)

        self.tab1 = ttk.Frame(self.notebook, padding=10)
        self.tab2 = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab1, text=" Chọn Cáp Điện & Vòng Lặp Sụt Áp ")
        self.notebook.add(self.tab2, text=" Tính Ngắn Mạch ")

        self.dung_tab_1()
        self.dung_tab_2()

        frame_kq = ttk.LabelFrame(self, text=" Báo Cáo Kết Quả Tính Toán & Đề Xuất Thiết Bị Công Nghiệp ", padding=8)
        frame_kq.pack(fill="both", expand=True, padx=12, pady=6)

        self.txt_result = tk.Text(frame_kq, height=9, font=("Consolas", 10), bg="#f8fafc")
        self.txt_result.pack(fill="both", expand=True)

    def dung_tab_1(self):
        frame_form = ttk.Frame(self.tab1)
        frame_form.pack(fill="x")

        ttk.Label(frame_form, text="Hệ thống điện:").grid(row=0, column=0, sticky="w", pady=4)
        self.cbo_phase = ttk.Combobox(
            frame_form, values=["3 Pha (380V)", "1 Pha (220V)"], state="readonly", width=16
        )
        self.cbo_phase.set("3 Pha (380V)")
        self.cbo_phase.grid(row=0, column=1, padx=8, pady=4)

        ttk.Label(frame_form, text="Vật liệu ruột cáp:").grid(row=0, column=2, sticky="w", pady=4)
        self.cbo_mat = ttk.Combobox(frame_form, values=["Đồng", "Nhôm"], state="readonly", width=16)
        self.cbo_mat.set("Đồng")
        self.cbo_mat.grid(row=0, column=3, padx=8, pady=4)

        ttk.Label(frame_form, text="Công suất tải P (kW):").grid(row=1, column=0, sticky="w", pady=4)
        self.ent_p = ttk.Entry(frame_form, width=18)
        self.ent_p.insert(0, "35")
        self.ent_p.grid(row=1, column=1, padx=8, pady=4)

        ttk.Label(frame_form, text="Điện áp định mức U (V):").grid(row=1, column=2, sticky="w", pady=4)
        self.ent_u = ttk.Entry(frame_form, width=18)
        self.ent_u.insert(0, "380")
        self.ent_u.grid(row=1, column=3, padx=8, pady=4)

        ttk.Label(frame_form, text="Hệ số công suất cosφ:").grid(row=2, column=0, sticky="w", pady=4)
        self.ent_cos = ttk.Entry(frame_form, width=18)
        self.ent_cos.insert(0, "0.85")
        self.ent_cos.grid(row=2, column=1, padx=8, pady=4)

        ttk.Label(frame_form, text="Chiều dài tuyến cáp L (m):").grid(row=2, column=2, sticky="w", pady=4)
        self.ent_l = ttk.Entry(frame_form, width=18)
        self.ent_l.insert(0, "250")
        self.ent_l.grid(row=2, column=3, padx=8, pady=4)

        btn_calc1 = tk.Button(
            frame_form, text="Chạy Vòng Lặp Đề Xuất Cáp & Kiểm Tra Sụt Áp",
            bg="#0284c7", fg="white", font=("Arial", 10, "bold"),
            padx=14, pady=4, command=self.xu_ly_tab_1
        )
        btn_calc1.grid(row=3, column=0, columnspan=4, pady=6)

        # Bảng truy vết các bước lặp tăng tiết diện cáp
        lbl_trace = ttk.Label(self.tab1, text="Bảng truy vết vòng lặp kiểm tra độ sụt áp (ΔU% <= 5%):", font=("Arial", 9, "bold"))
        lbl_trace.pack(anchor="w", pady=(4, 2))

        cols = ("buoc", "tiet_dien", "dong_cp", "sut_ap_v", "sut_ap_pt", "trang_thai")
        self.tree = ttk.Treeview(self.tab1, columns=cols, show="headings", height=3)
        self.tree.heading("buoc", text="Bước lặp")
        self.tree.heading("tiet_dien", text="Tiết diện thử")
        self.tree.heading("dong_cp", text="Icp phát nóng")
        self.tree.heading("sut_ap_v", text="Sụt áp ΔU (V)")
        self.tree.heading("sut_ap_pt", text="Sụt áp ΔU (%)")
        self.tree.heading("trang_thai", text="Đánh giá (Chuẩn <= 5%)")

        self.tree.column("buoc", width=70, anchor="center")
        self.tree.column("tiet_dien", width=100, anchor="center")
        self.tree.column("dong_cp", width=100, anchor="center")
        self.tree.column("sut_ap_v", width=100, anchor="center")
        self.tree.column("sut_ap_pt", width=100, anchor="center")
        self.tree.column("trang_thai", width=240, anchor="w")
        self.tree.pack(fill="x")

    def dung_tab_2(self):
        ttk.Label(self.tab2, text="Điện áp pha Up (V):").grid(row=0, column=0, sticky="w", pady=8)
        self.ent_up = ttk.Entry(self.tab2, width=18)
        self.ent_up.insert(0, "220")
        self.ent_up.grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(self.tab2, text="Tổng trở ngắn mạch ZΣ (Ω):").grid(row=0, column=2, sticky="w", pady=8)
        self.ent_z = ttk.Entry(self.tab2, width=18)
        self.ent_z.insert(0, "0.045")
        self.ent_z.grid(row=0, column=3, padx=8, pady=8)

        ttk.Label(self.tab2, text="Dòng tải làm việc Itt (A):").grid(row=1, column=0, sticky="w", pady=8)
        self.ent_itt = ttk.Entry(self.tab2, width=18)
        self.ent_itt.insert(0, "18.5")
        self.ent_itt.grid(row=1, column=1, padx=8, pady=8)

        btn_calc2 = tk.Button(
            self.tab2, text="Tính Dòng Ngắn Mạch Ink & Đề Xuất CB Bảo Vệ",
            bg="#0284c7", fg="white", font=("Arial", 10, "bold"),
            padx=14, pady=5, command=self.xu_ly_tab_2
        )
        btn_calc2.grid(row=2, column=0, columnspan=4, pady=12)

    def hien_thi_ket_qua(self, record):
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert(tk.END, format_record_as_text(record))
        self.app.cap_nhat_lich_su(record)

    def nhan_du_lieu_tu_dong_co(self, p_kw, u_v, cos_phi):
        self.notebook.select(self.tab1)
        self.cbo_phase.set("3 Pha (380V)")
        self.ent_p.delete(0, tk.END)
        self.ent_p.insert(0, str(p_kw))
        self.ent_u.delete(0, tk.END)
        self.ent_u.insert(0, str(u_v))
        self.ent_cos.delete(0, tk.END)
        self.ent_cos.insert(0, str(cos_phi))
        self.xu_ly_tab_1()

    def xu_ly_tab_1(self):
        try:
            he_dien = self.cbo_phase.get()
            vat_lieu = self.cbo_mat.get()
            p_kw = validate_float(self.ent_p.get(), "Công suất tải P (kW)")
            u_v = validate_float(self.ent_u.get(), "Điện áp định mức U (V)")
            cos_phi = validate_ratio(self.ent_cos.get(), "Hệ số công suất cosφ")
            l_m = validate_float(self.ent_l.get(), "Chiều dài tuyến cáp L (m)")

            results, equipment, bang_truy_vet = tinh_chon_cap_va_sut_ap(
                p_kw, u_v, cos_phi, l_m, he_dien, vat_lieu
            )

            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in bang_truy_vet:
                self.tree.insert("", tk.END, values=(
                    row["buoc"], row["tiet_dien"], row["dong_cp"],
                    row["sut_ap_v"], row["sut_ap_pt"], row["trang_thai"]
                ))

            inputs = {
                "Hệ thống & Vật liệu": f"{he_dien} - Cáp {vat_lieu}",
                "Thông số phụ tải": f"P = {p_kw} kW, U = {u_v} V, cosφ = {cos_phi}",
                "Chiều dài tuyến cáp": f"L = {l_m} m"
            }
            record = save_calculation_record(" Chọn cáp & Sụt áp", inputs, results, equipment)
            self.hien_thi_ket_qua(record)
        except ValueError as e:
            messagebox.showerror("Lỗi nhập liệu", str(e))

    def xu_ly_tab_2(self):
        try:
            up = validate_float(self.ent_up.get(), "Điện áp pha Up (V)")
            z_total = validate_float(self.ent_z.get(), "Tổng trở ngắn mạch ZΣ (Ω)")
            itt = validate_float(self.ent_itt.get(), "Dòng tải làm việc Itt (A)")

            results, equipment = tinh_ngan_mach_va_chon_cb(up, z_total, itt)
            inputs = {
                "Điện áp pha Up": f"{up} V",
                "Tổng trở ngắn mạch ZΣ": f"{z_total} Ω",
                "Dòng tải làm việc Itt": f"{itt} A"
            }
            record = save_calculation_record(" Tính ngắn mạch & Chọn CB", inputs, results, equipment)
            self.hien_thi_ket_qua(record)
        except ValueError as e:
            messagebox.showerror("Lỗi nhập liệu", str(e))
