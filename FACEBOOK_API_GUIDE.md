# Hướng Dẫn Sử Dụng Facebook Graph API

## Tại Sao Dùng API Thay Vì Selenium?

✅ **Ưu điểm:**
- Ổn định hơn (không bị lỗi UI, không cần chờ load trang)
- Nhanh hơn (upload trực tiếp qua API)
- Không cần mở browser
- Không bị Facebook phát hiện automation
- Dễ debug (có error message rõ ràng)

❌ **Nhược điểm:**
- Cần setup Access Token (1 lần)
- Cần quyền admin/editor của Page

---

## 🚀 CÁCH ĐƠN GIẢN NHẤT (Khuyên Dùng)

### Bước 1: Lấy Page Access Token

1. Truy cập: **https://developers.facebook.com/tools/explorer**

2. Ở góc trên bên phải:
   - Click dropdown **"Meta App"** → Chọn **"Graph API Explorer"** (hoặc để mặc định)
   - Click dropdown **"User or Page"** → Chọn **Page** bạn muốn đăng video

3. Click nút **"Generate Access Token"**

4. Popup hiện ra, tick các quyền sau:
   - ☑ `pages_manage_posts` (Bắt buộc - để đăng video)
   - ☑ `pages_read_engagement` (Tùy chọn - để xem thống kê)
   - ☑ `pages_show_list` (Tùy chọn - để list pages)

5. Click **"Generate Access Token"** → **"Continue"** → Đăng nhập nếu cần

6. **Copy token** hiện ra (dạng `EAAxxxx...`)

⚠️ **Lưu ý:** Token này chỉ tồn tại **1-2 giờ** (Short-lived). Xem bên dưới để lấy Long-lived token.

---

### Bước 2: Lấy Page ID

**Cách 1: Từ Graph API Explorer (Đang mở)**

1. Ở ô **"Query"**, xóa hết và gõ: `me?fields=id,name`
2. Click **"Submit"**
3. Kết quả hiện ra:
   ```json
   {
     "id": "123456789012345",
     "name": "Tên Page Của Bạn"
   }
   ```
4. Copy số `id` đó

**Cách 2: Từ URL Page**

1. Vào Page Facebook của bạn
2. Click **"About"** (Giới thiệu)
3. Kéo xuống phần **"Page ID"** hoặc **"Page transparency"**
4. Copy số Page ID

**Cách 3: Từ URL**

- Nếu URL là `facebook.com/YourPageName` → Vào About để xem ID
- Nếu URL là `facebook.com/profile.php?id=123456789` → `123456789` là Page ID

---

### Bước 3: Cấu Hình Tool

1. Mở tool → chọn Page (hoặc tạo Page mới)
2. Tick ☑ **"Dùng Facebook Graph API (thay vì Selenium)"**
3. Điền:
   - **Page ID**: `123456789012345` (từ Bước 2)
   - **Access Token**: `EAAxxxx...` (từ Bước 1)
4. Click **"Save Config"**
5. Import videos như bình thường
6. Click **"START AUTOMATION"**

Tool sẽ tự động:
- Test kết nối
- Upload từng video
- Set Tiêu đề = Mô tả = Tên file (không có đuôi .mp4)
- Schedule đúng ngày giờ bạn chọn

---

## 🔄 Lấy Long-Lived Token (60 ngày - Không cần làm lại mỗi 2 giờ)

Token từ Graph API Explorer chỉ tồn tại 1-2 giờ. Để lấy token tồn tại **60 ngày**:

### Cách 1: Dùng Python Script

```python
import requests

# Thay bằng token vừa lấy từ Graph API Explorer
short_token = "EAAxxxx..."

# Gọi API để exchange
url = "https://graph.facebook.com/v18.0/oauth/access_token"
params = {
    "grant_type": "fb_exchange_token",
    "client_id": "YOUR_APP_ID",  # Cần tạo App (xem bên dưới)
    "client_secret": "YOUR_APP_SECRET",
    "fb_exchange_token": short_token
}

response = requests.get(url, params=params)
print(response.json())
# Copy "access_token" từ kết quả
```

### Cách 2: Dùng Browser

```
https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_TOKEN
```

Thay `YOUR_APP_ID`, `YOUR_APP_SECRET`, `YOUR_SHORT_TOKEN` rồi paste vào browser.

⚠️ **Lưu ý:** Cần có App ID và App Secret (xem phần "Tạo Facebook App" bên dưới)

---

## 🔐 Lấy Permanent Token (Không hết hạn - Khuyên dùng nhất)

Sau khi có Long-lived token (60 ngày):

1. Vào Graph API Explorer: https://developers.facebook.com/tools/explorer
2. Paste Long-lived token vào ô **"Access Token"**
3. Ở ô Query, gõ: `me/accounts`
4. Click **"Submit"**
5. Kết quả hiện danh sách Pages:
   ```json
   {
     "data": [
       {
         "access_token": "EAAyyy...",  ← Token này KHÔNG HẾT HẠN
         "id": "123456789",
         "name": "Tên Page"
       }
     ]
   }
   ```
6. Copy `access_token` của Page bạn cần

✅ Token này **không hết hạn** (trừ khi bạn đổi password Facebook hoặc revoke quyền)

---

## 📱 Tạo Facebook App (Chỉ cần nếu muốn Long-lived Token)

Nếu bạn chỉ dùng Short-lived token (1-2 giờ) thì **KHÔNG CẦN** tạo App.

Nếu muốn Long-lived token (60 ngày) hoặc Permanent token:

1. Truy cập: https://developers.facebook.com/apps/create/
   
2. Nếu không thấy nút "Create App":
   - Click vào avatar góc phải → **"Developer Settings"**
   - Hoặc vào: https://developers.facebook.com/apps/
   - Click **"Create App"** (nút xanh)

3. Chọn loại App:
   - **"Business"** (nếu có) → Next
   - Hoặc **"Other"** → Next → **"Business"**

4. Điền thông tin:
   - **App Name**: "Video Scheduler" (tùy ý)
   - **App Contact Email**: Email của bạn
   - Click **"Create App"**

5. Vào **Dashboard** → Copy:
   - **App ID**: `1234567890`
   - **App Secret**: Click **"Show"** → Copy

6. Dùng App ID và App Secret để exchange token (xem phần "Lấy Long-Lived Token" ở trên)

---

## ✅ Test Kết Nối

Tool sẽ tự động test kết nối trước khi upload. Nếu thấy:
- ✓ **"Kết nối thành công! Page: [Tên Page]"** → OK, bắt đầu upload
- ❌ **"Lỗi kết nối"** → Kiểm tra lại Token hoặc Page ID

---

## 🐛 Troubleshooting

### Lỗi: "Invalid OAuth access token"
→ Token hết hạn hoặc sai. Lấy token mới từ Graph API Explorer.

### Lỗi: "Insufficient permissions"
→ Token thiếu quyền `pages_manage_posts`. Tạo lại token và nhớ tick quyền này.

### Lỗi: "Page not found" hoặc "(#100) Invalid parameter"
→ Page ID sai hoặc token không có quyền truy cập Page đó. Kiểm tra lại Page ID.

### Lỗi: "Application does not have permission for this action"
→ Bạn không phải Admin/Editor của Page. Cần có quyền quản lý Page.

### Video upload chậm
→ Bình thường, tùy kích thước video (có thể 1-5 phút/video). API sẽ log "Đang upload..." trong quá trình.

### Token hết hạn sau 1-2 giờ
→ Dùng Short-lived token. Lấy Long-lived (60 ngày) hoặc Permanent token (xem hướng dẫn ở trên).

---

## 📊 So Sánh: Selenium vs API

| Tính năng | Selenium | API |
|-----------|----------|-----|
| Tốc độ | Chậm (phải load UI) | Nhanh |
| Ổn định | Dễ lỗi (UI thay đổi) | Rất ổn định |
| Setup | Dễ (chỉ cần Chrome) | Cần Access Token |
| Bảo mật | Dễ bị phát hiện | An toàn |
| Debug | Khó (phải xem UI) | Dễ (có error message) |
| Mô tả | Khó điền (lỗi XPath) | Tự động = Tiêu đề |

**Khuyến nghị:** Dùng API cho production, Selenium chỉ khi không lấy được token.
