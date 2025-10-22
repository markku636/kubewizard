# Tests 目錄

這個目錄包含所有測試腳本。

## 📁 結構

```
tests/
├── __init__.py           # 測試模組初始化
├── test_units.py         # 單元測試
└── test_api.py           # API 測試
```

## 🧪 測試腳本

### test_units.py
**單元測試腳本**

測試核心功能模組：
- ✅ 配置管理測試
- ✅ KubeAgent 測試
- ✅ 記憶服務測試
- ✅ API 數據模型測試

**運行方式**:
```bash
# 從專案根目錄運行
python tests/test_units.py

# 或使用相對路徑
cd tests
python test_units.py
```

**預期輸出**:
```
============================================================
🧪 KubeWizard API 功能測試
============================================================

1. 測試配置...
   ✅ 配置正常
   
2. 測試 KubeAgent...
   ✅ KubeAgent 創建成功
   
3. 測試記憶服務...
   ✅ 記憶服務正常
   
4. 測試 API 模型...
   ✅ ChatRequest 正常
   ✅ ChatResponse 正常
   ✅ HealthResponse 正常

總計: 4/4 測試通過
🎉 所有測試通過！
```

### test_api.py
**API 端點測試腳本**

測試 FastAPI 端點：
- 🏠 根端點測試
- 💚 健康檢查測試
- 💬 聊天端點測試
- 🧠 記憶管理測試

**運行方式**:
```bash
# 終端 1: 啟動 API 服務器
python -m kubewizard_linebot.api

# 終端 2: 運行 API 測試
python tests/test_api.py
```

**注意**: API 測試需要先啟動 API 服務器。

## 🔧 如何添加新測試

### 1. 單元測試

在 `test_units.py` 中添加新的測試函數：

```python
def test_my_feature():
    """測試我的功能"""
    print("\n5. 測試我的功能...")
    try:
        from my_module import MyFeature
        
        feature = MyFeature()
        result = feature.do_something()
        
        assert result is not None, "結果不應為空"
        
        print(f"   ✅ 測試通過")
        return True
    except Exception as e:
        print(f"   ❌ 測試失敗: {e}")
        return False
```

然後在 `main()` 函數中添加：
```python
results.append(("我的功能", test_my_feature()))
```

### 2. API 測試

在 `test_api.py` 中添加新的測試：

```python
async def test_my_endpoint(session, base_url):
    """測試我的端點"""
    print("\n5. Testing my endpoint...")
    try:
        async with session.get(f"{base_url}/my-endpoint") as resp:
            assert resp.status == 200
            data = await resp.json()
            print(f"✅ My endpoint works: {data}")
    except Exception as e:
        print(f"❌ Error: {e}")
```

## 🎯 測試最佳實踐

### 測試結構
```python
def test_feature():
    """測試功能描述"""
    print("\nX. 測試 [功能名稱]...")
    try:
        # 1. 準備 (Arrange)
        setup_test_data()
        
        # 2. 執行 (Act)
        result = execute_function()
        
        # 3. 驗證 (Assert)
        assert result is not None
        assert result.status == "success"
        
        print(f"   ✅ 測試通過")
        return True
    except Exception as e:
        print(f"   ❌ 測試失敗: {e}")
        return False
```

### 斷言檢查
```python
# 基本斷言
assert value is not None
assert value == expected
assert len(items) > 0

# 類型檢查
assert isinstance(result, dict)
assert hasattr(obj, 'method_name')

# 異常處理
try:
    risky_operation()
except SpecificError:
    print("✅ 正確拋出異常")
else:
    raise AssertionError("應該拋出異常")
```

### 清理資源
```python
def test_with_cleanup():
    """測試並清理資源"""
    try:
        # 創建測試資源
        resource = create_test_resource()
        
        # 執行測試
        result = test_operation(resource)
        
        return result
    finally:
        # 無論成功失敗都清理
        cleanup_test_resource(resource)
```

## 📊 測試覆蓋率

目前測試覆蓋的模組：
- ✅ 配置管理 (config.py)
- ✅ KubeAgent (agents/kube_agent.py)
- ✅ 記憶服務 (kubewizard_linebot/memory.py)
- ✅ API 模型 (kubewizard_linebot/models.py)
- ✅ API 端點 (kubewizard_linebot/api.py, routers/)

待添加測試：
- ⏳ 工具函數 (tools/)
- ⏳ CLI 應用 (app/)
- ⏳ 更多 Agent (當添加新 Agent 時)

## 🚀 持續整合

測試可以集成到 CI/CD 流程中：

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: python tests/test_units.py
```

## 📚 相關資源

- [Python unittest](https://docs.python.org/3/library/unittest.html)
- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
