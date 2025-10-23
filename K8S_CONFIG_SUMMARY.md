# Kubernetes 環境兼容性配置總結

## 🎯 問題描述

需要讓 Python 應用程序能夠在以下兩種環境中運行:

1. **Kubernetes 集群內** - 使用 ServiceAccount (`load_incluster_config()`)
2. **本地開發環境** - 使用 kubeconfig 文件 (`~/.kube/config`)

## ✅ 解決方案

已實施自動環境檢測機制,應用程序會:
1. 首先嘗試載入集群內配置 (Pod 環境)
2. 如果失敗,則載入本地 kubeconfig 文件
3. 自動適配不同環境,無需手動切換

## 📁 新增文件

### 1. `utils/k8s_config.py` - Kubernetes 配置管理器
**功能:**
- 自動檢測運行環境 (K8s 或本地)
- 統一的配置載入接口
- 提供各種 API 客戶端 (CoreV1Api, AppsV1Api 等)
- 單例模式,避免重複載入

**核心類:**
- `K8sConfigManager` - 主要配置管理器
- `get_k8s_config_manager()` - 取得全域實例

### 2. `examples/k8s_client_example.py` - 使用範例
**包含範例:**
- 列出所有 Pod
- 列出命名空間
- 列出 Deployment
- 列出 Service
- 列出節點

### 3. `test_k8s_config.py` - 配置測試腳本
**功能:**
- 驗證配置是否正確載入
- 測試 API 連接
- 提供詳細的診斷信息

### 4. `docs/K8S_CONFIG_GUIDE.md` - 完整配置指南
**包含:**
- 本地環境配置
- Kubernetes 環境配置
- Docker 容器配置
- RBAC 權限配置
- 故障排除指南
- 最佳實踐

## 🔄 修改的文件

### 1. `requirements.txt`
**新增:**
```
kubernetes>=28.0.0
```

### 2. `tools/kubetool.py`
**修改:**
- 導入 `k8s_config` 模組
- 在初始化時自動載入 K8s 配置
- 添加環境檢測日誌

### 3. `Dockerfile`
**修改:**
- 修正目錄名稱 (`agent/` → `agents/`)
- 添加註釋說明 in-cluster config

## 📝 使用方法

### 本地開發環境

#### 方式 1: 使用環境變數 (推薦)

```powershell
# Windows PowerShell
$env:KUBECONFIG="$HOME\.kube\config"
python test_k8s_config.py
```

```bash
# Linux/macOS
export KUBECONFIG=~/.kube/config
python test_k8s_config.py
```

#### 方式 2: 使用 .env 文件

創建 `.env`:
```env
KUBECONFIG=~/.kube/config
```

#### 方式 3: 在代碼中使用

```python
from utils.k8s_config import get_k8s_config_manager

# 自動載入配置
k8s_manager = get_k8s_config_manager()
k8s_manager.load_config()

# 取得 API 客戶端
v1 = k8s_manager.get_core_v1_api()

# 列出 Pod
pods = v1.list_pod_for_all_namespaces()
for pod in pods.items:
    print(f"{pod.metadata.namespace} - {pod.metadata.name}")
```

### Kubernetes 環境

#### 使用 Helm 部署

```bash
# 安裝 (自動配置 RBAC)
helm install kubewizard ./helm

# 驗證
kubectl get pods -l app.kubernetes.io/name=kubewizard
kubectl logs -l app.kubernetes.io/name=kubewizard
```

#### 手動部署

1. **創建 ServiceAccount 和 RBAC**

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: kubewizard
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: kubewizard-role
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "namespaces", "nodes"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: kubewizard-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: kubewizard-role
subjects:
  - kind: ServiceAccount
    name: kubewizard
    namespace: default
```

2. **部署應用**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kubewizard
spec:
  replicas: 1
  template:
    spec:
      serviceAccountName: kubewizard  # 重要!
      containers:
      - name: kubewizard
        image: kubewizard:latest
```

### Docker 容器環境

```bash
# 構建鏡像
docker build -t kubewizard:latest .

# 使用本地 kubeconfig 運行
docker run -it --rm \
  -v ~/.kube/config:/root/.kube/config:ro \
  -e KUBECONFIG=/root/.kube/config \
  kubewizard:latest python test_k8s_config.py
```

## 🧪 測試步驟

### 1. 安裝依賴

```powershell
pip install -r requirements.txt
```

### 2. 配置環境變數

```powershell
$env:KUBECONFIG="$HOME\.kube\config"
```

### 3. 運行測試

```powershell
# 快速測試
python test_k8s_config.py

# 完整範例
python examples/k8s_client_example.py
```

### 4. 驗證輸出

**本地環境:**
```
✓ 成功載入 kubeconfig 配置: C:\Users\<user>\.kube\config
💻 環境類型: 本地環境 (使用 kubeconfig)
```

**K8s 環境:**
```
✓ 成功載入集群內配置 (運行在 K8s Pod 中)
🏢 環境類型: Kubernetes 集群內 (使用 ServiceAccount)
```

## 🔑 核心優勢

### 1. 自動環境檢測
無需手動判斷環境,程序自動選擇正確的配置方式

### 2. 統一接口
無論在哪種環境,代碼完全相同:

```python
k8s_manager = get_k8s_config_manager()
k8s_manager.load_config()
v1 = k8s_manager.get_core_v1_api()
```

### 3. 優雅降級
如果載入失敗,提供詳細的錯誤信息和建議

### 4. 安全性
- 本地使用 kubeconfig
- K8s 使用 ServiceAccount (更安全)
- 支持 RBAC 權限控制

### 5. 易於測試
提供完整的測試腳本和範例代碼

## 🔧 配置優先級

配置載入順序:

1. **In-Cluster Config** (最高優先級)
   - 檢測 `/var/run/secrets/kubernetes.io/serviceaccount/`
   - 適用於 Pod 環境

2. **指定的 kubeconfig 路徑**
   - `K8sConfigManager(kubeconfig_path="/path/to/config")`

3. **環境變數 KUBECONFIG**
   - `os.environ['KUBECONFIG']`

4. **預設路徑** (最低優先級)
   - `~/.kube/config`

## 📚 相關文檔

- **完整配置指南**: `docs/K8S_CONFIG_GUIDE.md`
- **使用範例**: `examples/k8s_client_example.py`
- **測試腳本**: `test_k8s_config.py`

## 🐛 故障排除

### 問題: 無法載入配置

**檢查清單:**
1. ✅ 是否安裝了 `kubernetes` 套件
2. ✅ 是否設定了 `KUBECONFIG` 環境變數
3. ✅ `~/.kube/config` 文件是否存在
4. ✅ kubectl 是否能正常工作

**解決方案:**
```powershell
# 1. 安裝依賴
pip install kubernetes

# 2. 設定環境變數
$env:KUBECONFIG="$HOME\.kube\config"

# 3. 驗證 kubectl
kubectl cluster-info

# 4. 運行測試
python test_k8s_config.py
```

### 問題: 權限被拒絕 (Forbidden)

在 K8s 環境中,確保:
1. ✅ ServiceAccount 已創建
2. ✅ ClusterRole 已定義
3. ✅ ClusterRoleBinding 已綁定
4. ✅ Deployment 中指定了 `serviceAccountName`

## 🎉 總結

現在您的應用程序已經可以:
- ✅ 在本地開發環境運行
- ✅ 在 Kubernetes 集群內運行
- ✅ 在 Docker 容器內運行
- ✅ 自動檢測並適配環境
- ✅ 提供統一的 API 接口
- ✅ 支持 RBAC 權限控制

無需修改代碼,同一個應用程序可以在不同環境無縫運行! 🚀
