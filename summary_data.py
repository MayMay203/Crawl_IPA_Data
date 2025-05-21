import os
import json
import google.generativeai as genai

# Cấu hình API key
genai.configure(api_key = os.getenv('OPENAI_API_KEY')) 

# Tạo model Gemini
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

input_dir = "Final_Output"

results = []

# Duyệt tất cả các file .md trong thư mục
for filename in os.listdir(input_dir):
    if filename.endswith(".md"):
        filepath = os.path.join(input_dir, filename)
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Prompt để tóm tắt
        prompt = f'Bạn hãy đọc đoạn văn bản dưới đây và tóm tắt lại nội dung chính, chỉ lấy phần văn bản chính, bỏ qua tất cả các link, địa chỉ URL, hình ảnh, biểu tượng, quảng cáo, các phần điều hướng hoặc nội dung không liên quan khác. Chỉ trả về phần nội dung văn bản thuần túy, ngắn gọn và súc tích. Đoạn văn bản: "{content}"'

        try:
            # Gửi lên Gemini
            response = model.generate_content(prompt)
            summary = response.text.strip()

            results.append({
                "url": filename.replace(".md", ""),
                "text": summary
            })

            print(f"Đã tóm tắt: {filename}")

        except Exception as e:
            print(f"Lỗi khi xử lý {filename}: {e}")

# Kiểm tra có file .json trong thư mục không, nếu có thì đọc và thêm vào results
for filename in os.listdir(input_dir):
    if filename.endswith(".json"):
        filepath = os.path.join(input_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Nếu data là list thì append từng phần tử
                if isinstance(data, list):
                    results.extend(data)
                # Nếu data là dict thì append trực tiếp
                elif isinstance(data, dict):
                    results.append(data)
                else:
                    print(f"Dữ liệu trong {filename} không phải list hoặc dict, bỏ qua.")
            print(f"Đã thêm dữ liệu từ file JSON: {filename}")
        except Exception as e:
            print(f"Lỗi khi đọc file JSON {filename}: {e}")

output_path = os.path.join(input_dir, "output.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("🎉 Hoàn tất! Kết quả đã ghi vào output.json")


# Trường hợp gemini quá request
# # Đọc dữ liệu đã có trong output.json nếu tồn tại
# if os.path.exists(output_path):
#     with open(output_path, "r", encoding="utf-8") as f:
#         try:
#             results = json.load(f)
#         except json.JSONDecodeError:
#             print("⚠️ output.json bị lỗi hoặc trống. Bắt đầu mới.")
#             results = []

# # Tạo danh sách URL đã xử lý
# existing_urls = {item["url"] for item in results if "url" in item}

# # Tên file muốn bắt đầu từ đó
# start_filename = "https_investdanang.gov.vn_web_guest_so-lieu-thong-ke.md"
# start_processing = False

# # Duyệt file .md
# for filename in os.listdir(input_dir):
#     print(filename)
#     if filename.endswith(".md"):
#         decoded_filename = urllib.parse.unquote(filename)
#         if decoded_filename == start_filename:
#             start_processing = True

#         if not start_processing:
#             continue  # bỏ qua cho đến khi gặp file bắt đầu

#         url_key = filename.replace(".md", "")
#         if url_key in existing_urls:
#             print(f"❎ Bỏ qua vì đã có: {filename}")
#             continue

#         filepath = os.path.join(input_dir, filename)
#         with open(filepath, "r", encoding="utf-8") as f:
#             content = f.read()

#         prompt = f'Bạn hãy đọc đoạn văn bản dưới đây và tóm tắt lại nội dung chính, chỉ lấy phần văn bản chính, bỏ qua tất cả các link, địa chỉ URL, hình ảnh, biểu tượng, quảng cáo, các phần điều hướng hoặc nội dung không liên quan khác. Chỉ trả về phần nội dung văn bản thuần túy, ngắn gọn và súc tích. Đoạn văn bản: "{content}"'

#         try:
#             response = model.generate_content(prompt)
#             summary = response.text.strip()

#             results.append({
#                 "url": url_key,
#                 "text": summary
#             })

#             print(f"✅ Đã tóm tắt: {filename}")

#         except Exception as e:
#             print(f"❌ Lỗi khi xử lý {filename}: {e}")

# # Ghi lại toàn bộ (bao gồm dữ liệu cũ + mới)
# with open(output_path, "w", encoding="utf-8") as f:
#     json.dump(results, f, ensure_ascii=False, indent=2)

# print("🎉 Hoàn tất! Dữ liệu đã được cập nhật vào output.json")