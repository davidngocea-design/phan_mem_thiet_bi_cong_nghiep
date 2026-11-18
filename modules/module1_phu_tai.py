"""
File: modules/module1_phu_tai.py
Chức năng: MODULE 1 - TÍNH TOÁN PHỤ TẢI & ĐỀ XUẤT THIẾT BỊ ĐÓNG CẮT / BÙ CÔNG SUẤT
Gồm 2 bài toán tương ứng với 2 Tab:
  - Tab 1 (Thành viên 1): Mạch 1 Pha & Tính Bù Công Suất Phản Kháng (Nâng cosφ) -> Đề xuất Tụ bù + CB.
  - Tab 2 (Thành viên 2): Động Cơ Không Đồng Bộ 3 Pha -> Đề xuất Contactor + Rơ le nhiệt.
"""

import math
from utils.history import load_catalog


# ==============================================================================
# TAB 1 (THÀNH VIÊN 1): MẠCH 1 PHA & BÙ CÔNG SUẤT PHẢN KHÁNG (cosφ)
# ==============================================================================
def tinh_phu_tai_1_pha_va_tu_bu(p_kw, u_v, cos_phi_1, cos_phi_2, f_hz=50.0):
    """
    Tính dòng điện, công suất Q, S của tải 1 pha và dung lượng tụ bù Qc cần thiết
    để nâng hệ số công suất từ cos_phi_1 lên cos_phi_2.
    """
    if cos_phi_2 <= cos_phi_1:
        raise ValueError(
            f"Lỗi logic: Hệ số cosφ mục tiêu ({cos_phi_2}) phải lớn hơn cosφ ban đầu ({cos_phi_1})!"
        )

    # 1. Tính thông số phụ tải 1 pha trước khi bù
    s_1_kva = p_kw / cos_phi_1
    i_1_a = (p_kw * 1000.0) / (u_v * cos_phi_1)

    phi_1 = math.acos(cos_phi_1)
    phi_2 = math.acos(cos_phi_2)

    q_1_kvar = p_kw * math.tan(phi_1)
    q_2_kvar = p_kw * math.tan(phi_2)

    # 2. Dung lượng tụ bù cần thiết Qc (kVAR) và điện dung C (µF)
    q_bu_kvar = q_1_kvar - q_2_kvar
    c_uf = (q_bu_kvar * 1e9) / (2.0 * math.pi * f_hz * (u_v ** 2))

    # 3. Tra bảng catalog.json đề xuất Tụ bù chuẩn và CB bảo vệ tụ
    catalog = load_catalog()
    ds_tu_bu = catalog["capacitors_kvar"]
    ds_mccb = catalog["mccb_ratings_a"]

    tu_chon = None
    for tu in ds_tu_bu:
        if tu >= q_bu_kvar:
            tu_chon = tu
            break

    if tu_chon is not None:
        de_xuat_tu = f"Tụ bù công nghiệp {tu_chon} kVAR (Yêu cầu tính toán: {q_bu_kvar:.2f} kVAR)"
        dong_tu_a = (tu_chon * 1000.0) / u_v
    else:
        so_bo_50 = math.ceil(q_bu_kvar / 50.0)
        de_xuat_tu = f"Ghép song song {so_bo_50} bộ tụ 50 kVAR (Tổng {so_bo_50 * 50} kVAR)"
        dong_tu_a = (q_bu_kvar * 1000.0) / u_v

    # Chọn CB bảo vệ tụ bù: I_CB >= 1.5 * I_tụ (chịu dòng xung nạp tụ và sóng hài)
    dong_cb_yeu_cau = 1.5 * dong_tu_a
    cb_chon = None
    for cb in ds_mccb:
        if cb >= dong_cb_yeu_cau:
            cb_chon = cb
            break

    if cb_chon is not None:
        de_xuat_cb = f"Aptomat MCCB {cb_chon} A (Chọn theo hệ số 1.5 × Itụ = {dong_cb_yeu_cau:.1f} A)"
    else:
        de_xuat_cb = f"Máy cắt công nghiệp >= {dong_cb_yeu_cau:.1f} A"

    results = {
        "Dòng điện tải 1 pha trước bù (I1)": f"{i_1_a:.2f} A",
        "Công suất biểu kiến (S1) / Phản kháng (Q1)": f"S1 = {s_1_kva:.2f} kVA  |  Q1 = {q_1_kvar:.2f} kVAR",
        "Dung lượng phản kháng cần bù (Qc)": f"{q_bu_kvar:.2f} kVAR",
        "Điện dung tụ bù tương đương (C)": f"{c_uf:.2f} µF",
        "Dòng điện định mức của nhánh tụ (Ic)": f"{dong_tu_a:.2f} A"
    }
    equipment = {
        "Tụ bù công suất phản kháng": de_xuat_tu,
        "Aptomat bảo vệ nhánh tụ bù": de_xuat_cb
    }
    return results, equipment


# ==============================================================================
# TAB 2 (THÀNH VIÊN 2): ĐỘNG CƠ KHÔNG ĐỒNG BỘ 3 PHA & CHỌN KHỞI ĐỘNG TỪ
# ==============================================================================
def tinh_dong_co_3_pha_va_khoi_dong_tu(p_kw, u_day, f_hz, so_doi_cuc_p, n_thuc_te, cos_phi, hieu_suat):
    """
    Tính tốc độ đồng bộ ns, độ trượt s%, mô-men xoắn M, dòng định mức Iđm
    và đề xuất bộ Khởi động từ (Contactor + Rơ le nhiệt).
    """
    n_dong_bo = (60.0 * f_hz) / so_doi_cuc_p

    # Lớp bảo vệ vật lý: Tốc độ rô-to thực tế phải nhỏ hơn tốc độ từ trường quay đồng bộ
    if n_thuc_te >= n_dong_bo:
        raise ValueError(
            f"Lỗi vật lý: Tốc độ quay thực tế n ({n_thuc_te} vòng/phút) "
            f"phải nhỏ hơn tốc độ đồng bộ ns ({n_dong_bo:.0f} vòng/phút)!"
        )

    do_truot_s = ((n_dong_bo - n_thuc_te) / n_dong_bo) * 100.0
    momen_m = 9550.0 * (p_kw / n_thuc_te)
    p_dien_kw = p_kw / hieu_suat
    i_dinh_muc = (p_kw * 1000.0) / (math.sqrt(3.0) * u_day * cos_phi * hieu_suat)

    # Tra bảng catalog.json chọn Contactor và Rơ le nhiệt
    catalog = load_catalog()
    ds_contactor = catalog["contactors"]
    ds_role = catalog["thermal_relays"]

    # 1. Chọn Contactor: I_đm_Contactor >= 1.25 * I_đm_động_cơ
    dong_yc_contactor = 1.25 * i_dinh_muc
    contactor_chon = None
    for c in ds_contactor:
        if c["rated_a"] >= dong_yc_contactor:
            contactor_chon = c["code"]
            break

    if contactor_chon is None:
        contactor_chon = f"Vượt dải 95A -> Cần chọn Contactor công suất lớn >= {dong_yc_contactor:.1f} A"

    # 2. Chọn Rơ le nhiệt: Dải dòng chỉnh định bao phủ dòng định mức động cơ (I_min <= Iđm <= I_max)
    role_chon = None
    for r in ds_role:
        if r["min_a"] <= i_dinh_muc <= r["max_a"]:
            role_chon = r["code"]
            break

    if role_chon is None:
        role_chon = f"Cần chọn Rơ le nhiệt có dải chỉnh chứa giá trị {i_dinh_muc:.2f} A"

    results = {
        "Tốc độ từ trường đồng bộ (ns)": f"{n_dong_bo:.0f} vòng/phút",
        "Hệ số trượt tốc độ (s%)": f"{do_truot_s:.2f} %",
        "Mô-men xoắn định mức trên trục (M)": f"{momen_m:.2f} N.m",
        "Công suất điện tiêu thụ (P1 = P/η)": f"{p_dien_kw:.2f} kW",
        "Dòng điện định mức động cơ (Iđm)": f"{i_dinh_muc:.2f} A"
    }
    equipment = {
        "Contactor điều khiển (I >= 1.25 × Iđm)": contactor_chon,
        "Rơ le nhiệt bảo vệ quá tải": role_chon
    }
    return results, equipment, p_dien_kw
