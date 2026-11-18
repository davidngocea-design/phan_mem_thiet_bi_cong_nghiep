"""
File: utils/validation.py
Chức năng: Kiểm tra dữ liệu người dùng nhập vào (Chặn để trống, nhập chữ, số âm, chia cho 0).
"""


def validate_float(value_str, field_name, allow_zero=False):
    """Kiểm tra và chuyển chuỗi nhập vào thành số thực (float)."""
    if value_str is None or str(value_str).strip() == "":
        raise ValueError(f"Ô '{field_name}' không được để trống!")

    text = str(value_str).strip().replace(",", ".")
    try:
        number = float(text)
    except ValueError:
        raise ValueError(f"Ô '{field_name}' phải nhập số hợp lệ (Đang nhập: '{value_str}')!")

    if allow_zero:
        if number < 0:
            raise ValueError(f"Ô '{field_name}' không được nhỏ hơn 0!")
    else:
        if number <= 0:
            raise ValueError(f"Ô '{field_name}' phải lớn hơn 0!")

    return number


def validate_int(value_str, field_name):
    """Kiểm tra và chuyển chuỗi nhập vào thành số nguyên dương (int)."""
    if value_str is None or str(value_str).strip() == "":
        raise ValueError(f"Ô '{field_name}' không được để trống!")

    text = str(value_str).strip()
    try:
        number = int(text)
    except ValueError:
        raise ValueError(f"Ô '{field_name}' phải là số nguyên (ví dụ: 1, 2, 3)!")

    if number <= 0:
        raise ValueError(f"Ô '{field_name}' phải lớn hơn 0!")

    return number


def validate_ratio(value_str, field_name):
    """Kiểm tra các hệ số cosφ, hiệu suất η nằm trong khoảng (0, 1]."""
    val = validate_float(value_str, field_name, allow_zero=False)

    if 1.0 < val <= 100.0:
        val = val / 100.0

    if val <= 0 or val > 1.0:
        raise ValueError(f"Ô '{field_name}' phải nằm trong khoảng từ 0.01 đến 1.0 (hoặc 1% - 100%)!")

    return val
