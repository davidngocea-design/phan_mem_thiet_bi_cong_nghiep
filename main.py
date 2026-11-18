"""
File chính: main.py
Tên đề tài: PHẦN MỀM TÍNH TOÁN VÀ ĐỀ XUẤT CÁC THIẾT BỊ CÔNG NGHIỆP
Cấu trúc: 2 Module chính x 2 Tab/Module = 4 Tab (Phân công đều cho 4 thành viên)
  - Module 1: Tính toán Phụ tải (Tab 1: Tụ bù cosφ | Tab 2: Động cơ 3 pha & Khởi động từ)
  - Module 2: Truyền tải & Bảo vệ (Tab 1: Chọn cáp & Sụt áp | Tab 2: Ngắn mạch & Chọn CB)
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from utils.history import load_history, clear_history
from utils.exporter import format_record_as_text, export_to_file
from views.module1_view import Module1PhuTaiView
from views.module2_view import Module2TruyenTaiView


class IndustrialDeviceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Phần mềm tính toán và đề xuất các thiết bị công nghiệp")
        self.geometry("1180x680")
        self.minsize(1020, 620)

        self.current_record = None
        self.history_records = []

        self.tao_bo_cuc_chinh()
        self.tai_danh_sach_lich_su()
        self.chuyen_module("mod1")

    def tao_bo_cuc_chinh(self):
        # 1. Thanh điều hướng bên trái (Sidebar gồm 2 Module chính)
        sidebar = tk.Frame(self, bg="#0f172a", width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        lbl_logo = tk.Label(
            sidebar,
            text="⚡ THIẾT BỊ CÔNG NGHIỆP\nTÍNH TOÁN & ĐỀ XUẤT",
            bg="#0c1222", fg="#38bdf8",
            font=("Arial", 12, "bold"), pady=20
        )
        lbl_logo.pack(fill="x")

        self.nav_buttons = {}
        ds_module = [
            ("mod1", "1. Tính Toán Phụ Tải\n   (Tụ Bù & Động Cơ 3 Pha)"),
            ("mod2", "2. Truyền Tải & Bảo Vệ\n   (Cáp Điện & Ngắn Mạch CB)")
        ]

        for ma_mod, ten_nut in ds_module:
            btn = tk.Button(
                sidebar, text=ten_nut, anchor="w", justify="left", padx=14, pady=12,
                bg="#1e293b", fg="white", font=("Arial", 10, "bold"),
                relief="flat", cursor="hand2",
                command=lambda k=ma_mod: self.chuyen_module(k)
            )
            btn.pack(fill="x", padx=10, pady=6)
            self.nav_buttons[ma_mod] = btn

        btn_export = tk.Button(
            sidebar, text="📄 Xuất Báo Cáo (.TXT/.CSV)",
            bg="#059669", fg="white", font=("Arial", 10, "bold"),
            pady=10, relief="flat", cursor="hand2",
            command=self.xuat_bao_cao
        )
        btn_export.pack(fill="x", padx=10, pady=(28, 6))

        # 2. Khung trung tâm chứa 2 Module
        self.center_container = ttk.Frame(self)
        self.center_container.pack(side="left", fill="both", expand=True)
        self.center_container.grid_rowconfigure(0, weight=1)
        self.center_container.grid_columnconfigure(0, weight=1)

        self.frames = {
            "mod1": Module1PhuTaiView(self.center_container, self),
            "mod2": Module2TruyenTaiView(self.center_container, self)
        }

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        # 3. Khung Lịch sử tính toán bên phải
        right_panel = ttk.LabelFrame(self, text=" Lịch Sử Tính Toán ", padding=8)
        right_panel.pack(side="right", fill="y", padx=8, pady=8)

        self.lst_history = tk.Listbox(right_panel, width=34, height=22, font=("Arial", 9))
        self.lst_history.pack(fill="both", expand=True, pady=4)
        self.lst_history.bind("<<ListboxSelect>>", self.xem_lai_lich_su)

        btn_clear = ttk.Button(right_panel, text="Xóa Lịch Sử", command=self.xoa_lich_su)
        btn_clear.pack(fill="x", pady=4)

    def chuyen_module(self, key):
        for k, btn in self.nav_buttons.items():
            btn.configure(bg="#0284c7" if k == key else "#1e293b")
        self.frames[key].tkraise()

    def chuyen_du_lieu_sang_module_2(self, p_kw, u_v, cos_phi):
        self.chuyen_module("mod2")
        self.frames["mod2"].nhan_du_lieu_tu_dong_co(p_kw, u_v, cos_phi)

    def tai_danh_sach_lich_su(self):
        self.history_records = load_history()
        self.lst_history.delete(0, tk.END)
        for rec in self.history_records:
            item_text = f"[{rec.get('Thời gian', '')[-8:]}] {rec.get('Tên bài toán', '')}"
            self.lst_history.insert(tk.END, item_text)

    def cap_nhat_lich_su(self, new_record):
        self.current_record = new_record
        self.tai_danh_sach_lich_su()

    def xem_lai_lich_su(self, event):
        sel = self.lst_history.curselection()
        if not sel:
            return
        idx = sel[0]
        rec = self.history_records[idx]
        self.current_record = rec
        messagebox.showinfo("Chi Tiết Lịch Sử Tính Toán", format_record_as_text(rec))

    def xoa_lich_su(self):
        if messagebox.askyesno("Xác nhận", "Bạn có muốn xóa toàn bộ lịch sử tính toán không?"):
            clear_history()
            self.tai_danh_sach_lich_su()

    def xuat_bao_cao(self):
        if not self.current_record:
            messagebox.showwarning("Chưa có dữ liệu", "Vui lòng thực hiện ít nhất 1 phép tính trước khi xuất báo cáo!")
            return

        filepath = filedialog.asksaveasfilename(
            title="Lưu Báo Cáo Kết Quả",
            defaultextension=".txt",
            filetypes=[("Text File (*.txt)", "*.txt"), ("Excel CSV (*.csv)", "*.csv")]
        )
        if filepath:
            export_to_file(self.current_record, filepath)
            messagebox.showinfo("Thành công", f"Đã xuất báo cáo thành công tại:\n{filepath}")


if __name__ == "__main__":
    app = IndustrialDeviceApp()
    app.mainloop()
