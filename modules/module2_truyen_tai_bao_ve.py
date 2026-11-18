"""
File: modules/module2_truyen_tai_bao_ve.py
Chức năng: MODULE 2 - TÍNH TOÁN TRUYỀN TẢI & ĐỀ XUẤT THIẾT BỊ BẢO VỆ
Gồm 2 bài toán tương ứng với 2 Tab:
  - Tab 1 (Thành viên 3): Chọn Cáp Điện & Vòng Lặp Kiểm Tra Sụt Áp (ΔU% <= 5%) -> Đề xuất Cáp & MCCB tổng.
  - Tab 2 (Thành viên 4): Tính Ngắn Mạch & Chọn Thiết Bị Đóng Cắt -> Đề xuất MCB/MCCB theo Iđm và dòng cắt Icu.
"""

import math
from utils.history import load_catalog


# ==============================================================================
# TAB 1 (THÀNH VIÊN 3): CHỌN CÁP ĐIỆN & VÒNG LẶP KIỂM TRA SỤT ÁP (ΔU% <= 5%)
# ==============================================================================
def tinh_chon_cap_va_sut_ap(p_kw, u_v, cos_phi, chieu_dai_m, he_dien="3 Pha (380V)", vat_lieu="Đồng"):
    """
    Quy trình 3 bước chọn cáp công nghiệp:
    - Bước 1: Tính dòng điện làm việc Itt và chọn MCCB tổng (I_MCCB >= 1.25 * Itt)
    - Bước 2: Tìm cỡ cáp khởi điểm thỏa điều kiện phát nóng lâu dài (I_cp_dây >= I_MCCB)
    - Bước 3: Chạy vòng lặp for kiểm tra độ sụt áp ΔU%. Nếu > 5% thì tự động tăng cỡ cáp.
    """
    catalog = load_catalog()
    ds_mccb = catalog["mccb_ratings_a"]
    ds_cap = catalog["cables"]

    # Bước 1: Tính dòng điện làm việc Itt và chọn MCCB
    if "3 Pha" in he_dien:
        i_tt = (p_kw * 1000.0) / (math.sqrt(3.0) * u_v * cos_phi)
        he_so_k = math.sqrt(3.0)
    else:
        i_tt = (p_kw * 1000.0) / (u_v * cos_phi)
        he_so_k = 2.0

    i_yc_mccb = 1.25 * i_tt
    mccb_chon = None
    for mccb in ds_mccb:
        if mccb >= i_yc_mccb:
            mccb_chon = mccb
            break

    # Bước 2: Tìm cỡ cáp khởi điểm theo điều kiện phát nóng
    if vat_lieu == "Đồng":
        rho = 0.0172
        cot_dong_cp = "cu_ampacity_a"
    else:
        rho = 0.0280
        cot_dong_cp = "al_ampacity_a"

    dong_phat_nong_yc = mccb_chon if mccb_chon is not None else i_yc_mccb

    vi_tri_bat_dau = len(ds_cap) - 1
    for i in range(len(ds_cap)):
        if ds_cap[i][cot_dong_cp] >= dong_phat_nong_yc:
            vi_tri_bat_dau = i
            break

    # Bước 3: Vòng lặp kiểm tra độ sụt áp ΔU% <= 5%
    bang_truy_vet = []
    cap_cuoi = ds_cap[-1]
    delta_u_v_cuoi = 0.0
    delta_u_pt_cuoi = 0.0
    dat_chuan = False

    for i in range(vi_tri_bat_dau, len(ds_cap)):
        cap_dang_xet = ds_cap[i]
        tiet_dien_s = cap_dang_xet["section_mm2"]
        dong_cho_phep = cap_dang_xet[cot_dong_cp]

        r_day = rho * (chieu_dai_m / tiet_dien_s)
        delta_u_v = he_so_k * i_tt * r_day * cos_phi
        delta_u_pt = (delta_u_v / u_v) * 100.0

        if delta_u_pt <= 5.0:
            trang_thai = "ĐẠT CHUẨN (<= 5%)"
            dat_chuan = True
        else:
            trang_thai = "KHÔNG ĐẠT (> 5%) -> Tăng cỡ cáp"

        bang_truy_vet.append({
            "buoc": len(bang_truy_vet) + 1,
            "tiet_dien": f"{tiet_dien_s} mm²",
            "dong_cp": f"{dong_cho_phep} A",
            "sut_ap_v": f"{delta_u_v:.2f} V",
            "sut_ap_pt": f"{delta_u_pt:.2f} %",
            "trang_thai": trang_thai
        })

        cap_cuoi = cap_dang_xet
        delta_u_v_cuoi = delta_u_v
        delta_u_pt_cuoi = delta_u_pt

        if dat_chuan:
            break

    s_chon = cap_cuoi["section_mm2"]
    i_cp_chon = cap_cuoi[cot_dong_cp]

    if dat_chuan:
        de_xuat_cap = f"Cáp {vat_lieu} tiết diện {s_chon} mm² (Icp = {i_cp_chon} A, Sụt áp = {delta_u_pt_cuoi:.2f}%)"
    else:
        de_xuat_cap = (
            f"Cảnh báo: Cáp lớn nhất 240 mm² vẫn sụt áp {delta_u_pt_cuoi:.2f}% (> 5%) "
            f"-> Đề xuất đi cáp chập đôi (2 sợi song song mỗi pha)!"
        )

    results = {
        "Hệ thống đường dây": f"{he_dien} - Ruột dẫn {vat_lieu}",
        "Dòng điện tính toán (Itt)": f"{i_tt:.2f} A",
        "Dòng yêu cầu bảo vệ (1.25 × Itt)": f"{i_yc_mccb:.2f} A",
        "Độ sụt áp trên cáp đã chọn (ΔU)": f"{delta_u_v_cuoi:.2f} V ({delta_u_pt_cuoi:.2f} %)",
        "Số bước lặp kiểm tra tiết diện": f"{len(bang_truy_vet)} bước"
    }
    equipment = {
        "Aptomat bảo vệ đầu tuyến (MCCB)": (
            f"MCCB {mccb_chon} A" if mccb_chon else f"Máy cắt ACB >= {i_yc_mccb:.0f} A"
        ),
        "Cáp điện lực đề xuất": de_xuat_cap
    }
    return results, equipment, bang_truy_vet


# ==============================================================================
# TAB 2 (THÀNH VIÊN 4): TÍNH NGẮN MẠCH & ĐỀ XUẤT THIẾT BỊ ĐÓNG CẮT (MCB / MCCB)
# ==============================================================================
def tinh_ngan_mach_va_chon_cb(u_pha, z_ngan_mach, i_tai):
    """
    Tính dòng điện ngắn mạch Ink = Up / Z_ngắn_mạch
    và đề xuất Aptomat thỏa mãn cả 2 điều kiện:
      1. Dòng định mức: I_đm >= 1.25 * I_tải
      2. Khả năng cắt ngắn mạch: I_cu (kA) >= I_nk (kA)
    """
    i_nk_a = u_pha / z_ngan_mach
    i_nk_ka = i_nk_a / 1000.0
    dong_yc_cb = 1.25 * i_tai

    catalog = load_catalog()
    ds_mcb = catalog["mcb_ratings_a"]
    ds_mccb = catalog["mccb_ratings_a"]
    ds_icu = catalog["mcb_icu_ka"]

    # 1. Chọn dòng định mức MCB / MCCB
    mcb_chon = None
    for mcb in ds_mcb:
        if mcb >= dong_yc_cb:
            mcb_chon = mcb
            break

    if mcb_chon is not None:
        de_xuat_cb = f"Aptomat MCB {mcb_chon} A (Yêu cầu >= 1.25 × Itt = {dong_yc_cb:.2f} A)"
    else:
        mccb_chon = None
        for mccb in ds_mccb:
            if mccb >= dong_yc_cb:
                mccb_chon = mccb
                break
        if mccb_chon is not None:
            de_xuat_cb = f"Vượt dải MCB 125A -> Đề xuất dùng MCCB công nghiệp {mccb_chon} A"
        else:
            de_xuat_cb = f"Phụ tải rất lớn -> Đề xuất dùng Máy cắt không khí ACB >= {dong_yc_cb:.0f} A"

    # 2. Chọn khả năng cắt ngắn mạch chuẩn Icu (kA)
    icu_chon = None
    for icu in ds_icu:
        if icu >= i_nk_ka:
            icu_chon = icu
            break

    if icu_chon is not None:
        de_xuat_icu = f"Chuẩn dòng cắt Icu = {icu_chon} kA (Lớn hơn dòng ngắn mạch Ink = {i_nk_ka:.2f} kA)"
    else:
        de_xuat_icu = f"Ngắn mạch cực đại ({i_nk_ka:.2f} kA > 50 kA) -> Cần dùng ACB/MCCB dòng cắt cao"

    results = {
        "Dòng điện ngắn mạch (A)": f"{i_nk_a:.2f} A",
        "Dòng điện ngắn mạch Ink (kA)": f"{i_nk_ka:.3f} kA",
        "Dòng định mức CB tối thiểu (1.25 × Itt)": f"{dong_yc_cb:.2f} A"
    }
    equipment = {
        "Thiết bị đóng cắt đề xuất (CB)": de_xuat_cb,
        "Khả năng cắt ngắn mạch (Icu)": de_xuat_icu
    }
    return results, equipment
