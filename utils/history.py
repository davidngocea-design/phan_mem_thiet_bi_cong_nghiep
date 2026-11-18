"""
File: utils/history.py
Chức năng: Đọc danh mục thiết bị từ data/catalog.json và lưu lịch sử vào data/history.json.
"""

import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CATALOG_FILE = os.path.join(DATA_DIR, "catalog.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")


def load_catalog():
    """Đọc dữ liệu thiết bị công nghiệp chuẩn từ file catalog.json."""
    with open(CATALOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_history():
    """Đọc danh sách lịch sử tính toán."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_calculation_record(module_name, inputs, results, equipment):
    """Lưu kết quả vừa tính vào đầu danh sách lịch sử (tối đa 30 bản ghi)."""
    os.makedirs(DATA_DIR, exist_ok=True)
    history = load_history()

    record = {
        "Thời gian": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "Tên bài toán": module_name,
        "Thông số đầu vào": inputs,
        "Kết quả tính toán": results,
        "Đề xuất thiết bị công nghiệp": equipment
    }

    history.insert(0, record)
    history = history[:30]

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    return record


def clear_history():
    """Xóa toàn bộ lịch sử tính toán."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)
