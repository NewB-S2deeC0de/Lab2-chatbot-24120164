

# Chatbot - 24120164

Hệ thống chatbot sử dụng mô hình llama3.2:1b, với logic Backend được xây dựng bằng FastAPI, giao diện Frontend được xây dựng bằng streamlit

## 🚀 Tính năng

* Giao diện người dùng (UI):
* **Xác thực người dùng trước khi vào chat**
* **Lưu và tải dữ liệu chat**
* Lịch sử được lưu theo phiên (session-based)
* Dễ dàng thay đổi mô hình hoặc thêm API tính năng khác

## 🧰 Requirements

* Python 3.x
* Các thư viện trong file `requirements.txt`

## ⚙️ Installation

```bash
git clone https://github.com/NewB-S2deeC0de/Lab2-chatbot-24120164.git
pip install -r requirements.txt
```

## 🛠️ Hướng dẫn chạy frontend

```bash
streamlit run frontend/app.py
```

## 🛠️ Hướng dẫn chạy backend
```bash
uvicorn backend.main:app --reload
```

## 🎬 Video demo
https://youtu.be/fOe2dQaQ6sk
