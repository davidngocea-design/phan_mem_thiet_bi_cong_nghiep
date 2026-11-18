"""
File: utils/exporter.py
Chức năng: Chuyển bản ghi kết quả thành văn bản Tiếng Việt và xuất ra file .TXT hoặc .CSV.
"""

import csv


def format_record_as_text(record):
    """Định dạng kết quả thành chuỗi văn bản hiển thị lên màn hình."""
    lines = []
    lines.append("=" * 70)
    lines.append("   PHẦN MỀM TÍNH TOÁN VÀ ĐỀ XUẤT CÁC THIẾT BỊ CÔNG NGHIỆP")
    lines.append("=" * 70)
    lines.append(f"Thời gian    : {record.get('Thời gian', '')}")
    lines.append(f"Tên bài toán : {record.get('Tên bài toán', '')}")
    lines.append("-" * 70)

    lines.append("1. THÔNG SỐ ĐẦU VÀO:")
    for key, val in record.get("Thông số đầu vào", {}).items():
        lines.append(f"   - {key}: {val}")

    lines.append("")
    lines.append("2. KẾT QUẢ TÍNH TOÁN:")
    for key, val in record.get("Kết quả tính toán", {}).items():
        lines.append(f"   - {key}: {val}")

    lines.append("")
    lines.append("3. ĐỀ XUẤT THIẾT BỊ CÔNG NGHIỆP:")
    for key, val in record.get("Đề xuất thiết bị công nghiệp", {}).items():
        lines.append(f"   * {key}: {val}")

    lines.append("=" * 70)
    return "\n".join(lines)


def export_to_file(record, filepath):
    """Lưu kết quả ra file .TXT hoặc .CSV."""
    if filepath.lower().endswith(".csv"):
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Nhóm thông tin", "Tên thông số", "Giá trị"])
            writer.writerow(["Thông tin chung", "Thời gian", record.get("Thời gian", "")])
            writer.writerow(["Thông tin chung", "Tên bài toán", record.get("Tên bài toán", "")])

            for k, v in record.get("Thông số đầu vào", {}).items():
                writer.writerow(["1. Thông số đầu vào", k, v])
            for k, v in record.get("Kết quả tính toán", {}).items():
                writer.writerow(["2. Kết quả tính toán", k, v])
            for k, v in record.get("Đề xuất thiết bị công nghiệp", {}).items():
                writer.writerow(["3. Đề xuất thiết bị công nghiệp", k, v])
    else:
        text_content = format_record_as_text(record)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text_content)
