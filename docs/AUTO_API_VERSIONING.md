# Auto API Versioning

## 🚀 Tính năng tự động

Hệ thống **TỰ ĐỘNG** quét và đăng ký tất cả API versions!

## 📁 Cấu trúc

```
routes/
├── v1/              # ✅ Tự động đăng ký
│   ├── __init__.py  # Phải có api_v1 blueprint
│   ├── auth.py
│   ├── users.py
│   └── posts.py
├── v2/              # ✅ Tự động đăng ký
│   ├── __init__.py  # Phải có api_v2 blueprint
│   └── auth.py
├── v3/              # ✅ Tự động đăng ký
│   ├── __init__.py  # Phải có api_v3 blueprint
│   └── auth.py
└── api_versions.py  # Auto-discovery engine
```

## ✨ Thêm version mới - CHỈ 3 BƯỚC

### Ví dụ: Thêm v4

#### 1. Tạo folder và __init__.py

```bash
mkdir routes/v4
```

```python
# routes/v4/__init__.py
from flask import Blueprint

api_v4 = Blueprint('api_v4', __name__, url_prefix='/api/v4')

from . import auth  # Import routes

__all__ = ['api_v4']
```

#### 2. Tạo routes (optional)

```python
# routes/v4/auth.py
from routes.v4 import api_v4

@api_v4.route("/auth/register", methods=["POST"])
def register():
    return {"message": "V4 API"}
```

#### 3. Restart server

```bash
python app.py
```

**DONE!** ✅ Tự động có `/api/v4/auth/register`

## 🎯 Quy tắc Auto-register

### ✅ SẼ được đăng ký nếu:

1. Folder tên `v` + số (v1, v2, v3, v99...)
2. Có file `__init__.py`
3. Có blueprint tên `api_v1`, `api_v2`, `api_v3`...

### ❌ KHÔNG được đăng ký nếu:

- Folder không bắt đầu bằng `v` (ví dụ: `admin`, `test`)
- Không có `__init__.py`
- Không có blueprint đúng tên

## 📊 Kiểm tra versions

```bash
# List all registered versions
curl http://localhost:8888/api/versions
```

Response:
```json
{
  "versions": [
    {
      "version": "v1",
      "base_url": "/api/v1",
      "status": "stable"
    },
    {
      "version": "v2",
      "base_url": "/api/v2",
      "status": "beta"
    },
    {
      "version": "v3",
      "base_url": "/api/v3",
      "status": "beta"
    }
  ],
  "latest": "v1",
  "recommended": "v1",
  "total": 3
}
```

## 🔥 Ưu điểm

1. **Zero config** - Tạo folder là tự động có
2. **Không cần sửa code** - Không cần edit `api_versions.py`
3. **Scale dễ dàng** - Thêm v99 cũng tự động
4. **Clean structure** - Mỗi version độc lập

## 📝 Blueprint naming convention

**QUAN TRỌNG:** Blueprint name phải match folder name:

- Folder `v1` → Blueprint `api_v1`
- Folder `v2` → Blueprint `api_v2`
- Folder `v10` → Blueprint `api_v10`

```python
# ✅ ĐÚNG
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# ❌ SAI - Tên không match
api_auth = Blueprint('api_auth', __name__, url_prefix='/api/v1')
```

## 🧪 Test

```bash
# Start server
python app.py

# Test v1
curl -X POST http://localhost:8888/api/v1/auth/register

# Test v2
curl -X POST http://localhost:8888/api/v2/auth/register

# Test v3 (auto-registered!)
curl -X POST http://localhost:8888/api/v3/auth/register

# List all versions
curl http://localhost:8888/api/versions
```

## 🎨 Customize version status

Muốn đánh dấu deprecated? Sửa trong `api_versions.py`:

```python
status = "deprecated" if version_name == "v1" else \
         "stable" if version_name == "v2" else \
         "beta"
```

## 💡 Tips

1. **v1 luôn là stable** - Production ready
2. **v2+ là beta** - Testing/preview
3. **Xóa folder = disable version** - Đơn giản!
4. **No restart needed** - Hot reload trong dev mode

That's it! Hệ thống tự động lo hết! 🚀
