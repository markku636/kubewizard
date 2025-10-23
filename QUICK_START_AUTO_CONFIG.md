# Kubernetes 配置自動載入 - 快速使用指南

## 🎯 改動摘要

已將專案中所有 Kubernetes 相關的配置載入統一為自動檢測模式：
- ✅ **在 K8s Pod 內**: 自動使用 ServiceAccount (`load_incluster_config()`)
- ✅ **在本地環境**: 自動使用 kubeconfig 文件 (`~/.kube/config`)

## 📦 修改的文件

### 1. **核心組件**
- `utils/k8s_config.py` - K8s 配置管理器（已存在，無需修改）
- `tools/kubetool.py` - 已整合配置管理器

### 2. **應用程序**
- `agents/kube_agent.py` - KubeAgent 初始化時自動載入配置
- `main.py` - 添加日誌配置
- `kubewizard_linebot/api.py` - API 啟動時自動載入配置

### 3. **範例和測試**
- `examples/demo_kubetool.py` - KubeTool 完整使用範例（新增）
- `test_auto_config.py` - 自動配置測試腳本（新增）

## 🚀 快速開始

### 本地環境（Windows PowerShell）

```powershell
# 1. 設定環境變數
$env:KUBECONFIG="$HOME\.kube\config"

# 2. 測試配置
python test_auto_config.py

# 3. 運行範例
python examples/demo_kubetool.py

# 4. 啟動主程序
python main.py
```

### 本地環境（Linux/macOS）

```bash
# 1. 設定環境變數
export KUBECONFIG=~/.kube/config

# 2. 測試配置
python test_auto_config.py

# 3. 運行範例
python examples/demo_kubetool.py

# 4. 啟動主程序
python main.py
```

### Kubernetes 環境

直接部署即可，無需額外配置：

```bash
# 使用 Helm
helm install kubewizard ./helm

# 檢查日誌
kubectl logs -l app.kubernetes.io/name=kubewizard
```

## 💻 程式碼使用方式

### 方式 1: 使用 KubeTool 執行 kubectl 命令

```python
from tools.kubetool import KubeTool

# 自動載入配置
tool = KubeTool()

# 執行命令
result = tool.invoke({"commands": "kubectl get pods -A"})
print(result)
```

### 方式 2: 直接使用 Kubernetes Python API

```python
from utils.k8s_config import get_k8s_config_manager

# 載入配置
manager = get_k8s_config_manager()
manager.load_config()

# 使用 API
v1 = manager.get_core_v1_api()
pods = v1.list_pod_for_all_namespaces()

for pod in pods.items:
    print(f"{pod.metadata.namespace}/{pod.metadata.name}")
```

### 方式 3: 在 KubeAgent 中使用

```python
from agents import KubeAgent

# KubeAgent 會在初始化時自動載入配置
agent = KubeAgent(user_id="your_user_id")

# 使用 agent
response = agent.invoke("列出所有 Pod")
print(response)
```

## 🔍 配置載入邏輯

配置管理器會按以下順序嘗試載入：

```
1. 檢測是否在 Pod 內
   └─ 是 → 使用 load_incluster_config()
   └─ 否 → 繼續下一步

2. 檢查建構時指定的 kubeconfig_path
   └─ 有 → 使用指定路徑
   └─ 無 → 繼續下一步

3. 檢查環境變數 KUBECONFIG
   └─ 有 → 使用環境變數路徑
   └─ 無 → 繼續下一步

4. 使用預設路徑 ~/.kube/config
```

## 📝 日誌輸出範例

### 本地環境啟動

```
2025-10-23 10:00:00 - INFO - ✓ Kubernetes 配置已載入 (本地環境)
2025-10-23 10:00:01 - INFO - KubeTool: 使用本地 kubeconfig 配置
```

### K8s 環境啟動

```
2025-10-23 10:00:00 - INFO - ✓ Kubernetes 配置已載入 (集群內環境)
2025-10-23 10:00:01 - INFO - KubeTool: 使用集群內配置 (Pod 環境)
```

## 🧪 測試步驟

### 1. 快速測試配置

```powershell
python test_auto_config.py
```

**預期輸出:**
```
✅ 配置管理器: 通過
✅ KubeTool: 通過
✅ KubeAgent: 通過
✅ Python API: 通過
🎉 所有測試通過！
```

### 2. 測試 KubeTool 功能

```powershell
python examples/demo_kubetool.py
```

### 3. 測試完整 Kubernetes 功能

```powershell
python examples/k8s_client_example.py
```

## ⚙️ 環境變數配置

### 必要的環境變數

```env
# Kubernetes 配置 (本地環境)
KUBECONFIG=~/.kube/config

# AI 配置 (使用 KubeAgent 時需要)
AI_GOOGLE_API_KEY=your-api-key
AI_MODEL=gemini-2.0-flash
AI_TEMPERATURE=0.7

# Redis 配置 (可選)
REDIS_URL=redis://localhost:6379/0

# 日誌級別 (可選)
LOG_LEVEL=INFO
```

### 創建 .env 文件

```powershell
# 創建 .env 文件
@"
KUBECONFIG=$HOME\.kube\config
AI_GOOGLE_API_KEY=your-api-key-here
AI_MODEL=gemini-2.0-flash
AI_TEMPERATURE=0.7
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
"@ | Out-File -FilePath .env -Encoding utf8
```

## 🐛 故障排除

### 問題 1: 找不到 kubeconfig

**錯誤:**
```
ConfigException: unable to load configuration
```

**解決方案:**
```powershell
# 檢查文件是否存在
Test-Path "$HOME\.kube\config"

# 設定環境變數
$env:KUBECONFIG="$HOME\.kube\config"

# 驗證 kubectl
kubectl cluster-info
```

### 問題 2: 無法連接集群

**錯誤:**
```
Unable to connect to the server
```

**解決方案:**
```powershell
# 檢查 kubectl 配置
kubectl config view

# 檢查當前上下文
kubectl config current-context

# 測試連接
kubectl get nodes
```

### 問題 3: 權限被拒絕 (在 K8s 中)

**錯誤:**
```
Forbidden: User "system:serviceaccount:default:kubewizard" cannot list pods
```

**解決方案:**
```bash
# 檢查 ServiceAccount
kubectl get serviceaccount kubewizard

# 檢查 RBAC
kubectl get clusterrolebinding kubewizard-binding

# 重新部署 (使用 Helm 會自動配置 RBAC)
helm upgrade --install kubewizard ./helm
```

## 📚 更多資源

- **完整配置指南**: `docs/K8S_CONFIG_GUIDE.md`
- **使用範例**: `examples/demo_kubetool.py`
- **測試腳本**: `test_auto_config.py`
- **配置測試**: `test_k8s_config.py`

## ✅ 檢查清單

部署前確認：

- [ ] 已安裝 `kubernetes` Python 套件
- [ ] kubectl 已安裝並可用
- [ ] 本地環境已設定 KUBECONFIG
- [ ] 已執行 `test_auto_config.py` 驗證
- [ ] K8s 環境已配置 ServiceAccount 和 RBAC

---

**🎉 完成！** 現在你的應用程序可以在本地和 Kubernetes 環境無縫運行了。
