import json
from urllib.parse import unquote

def restore_url(url):
    if url.startswith("https://") or url.startswith("http://"):
        return url
    
    if url.startswith("https_"):
        url = url.replace("https_", "https://", 1)
    elif url.startswith("http_"):
        url = url.replace("http_", "http://", 1)

    query_start = None
    for key in ["_dinhdanh=", "_id=", "_cat=", "_page=", "_lang=", "_ref=", "_tab=", "_keyword=", "_danhmuc="]:
        if key in url:
            query_start = url.find(key)
            break
    
    if query_start is not None:
        base = url[:query_start]
        query = url[query_start + 1:]  # bỏ dấu "_" đầu tiên
        base = base.replace("_", "/")
        restored_url = f"{base}?{query}"
    else:
        restored_url = url.replace("_", "/")

    return unquote(restored_url)


def restore_urls_in_json(input_json_path):
    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for item in data:
        if "url" in item:
            original_url = item["url"]
            new_url = restore_url(original_url)
            item["url"] = new_url  # Cập nhật url ngay trong dict
    
    # Ghi đè file JSON với dữ liệu đã update
    with open(input_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Đã hồi phục và cập nhật URL trong file {input_json_path}")


if __name__ == "__main__":
    input_json_file = "Final_Output/output.json"
    restore_urls_in_json(input_json_file)
