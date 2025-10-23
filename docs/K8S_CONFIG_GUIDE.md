# Kubernetes 環境配置指南

本指南說明如何配置 KubeWizard 在不同環境下運行。

## 📋 目錄

- [環境類型](#環境類型)
- [本地開發環境](#本地開發環境)
- [Kubernetes 集群環境](#kubernetes-集群環境)
- [Docker 容器環境](#docker-容器環境)
- [配置優先級](#配置優先級)
- [故障排除](#故障排除)

---

## 🌍 環境類型

KubeWizard 支援兩種運行環境:

### 1. 本地環境 (開發環境)
- 使用本地的 `~/.kube/config` 文件
- 適合開發和測試
- 需要手動配置 kubectl 訪問權限

### 2. Kubernetes 集群環境 (生產環境)
- 使用 Pod 內的 ServiceAccount 憑證
- 自動從 `/var/run/secrets/kubernetes.io/serviceaccount/` 讀取
- 需要配置適當的 RBAC 權限

---

## 💻 本地開發環境

### 前置要求

1. 安裝 kubectl
2. 配置 kubeconfig 文件

### 配置方式

#### 方式 1: 使用預設路徑 (推薦)

```bash
# Linux/macOS
export KUBECONFIG=~/.kube/config

# Windows PowerShell
$env:KUBECONFIG="$HOME\.kube\config"
```

#### 方式 2: 使用自定義路徑

```bash
# Linux/macOS
export KUBECONFIG=/path/to/your/kubeconfig

# Windows PowerShell
$env:KUBECONFIG="D:\configs\my-cluster-config.yaml"
```

#### 方式 3: 在 `.env` 文件中配置

創建 `.env` 文件:

```env
KUBECONFIG=~/.kube/config
```

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 測試連接

```bash
# 測試 kubectl 連接
kubectl get nodes

# 運行 Python 範例
python examples/k8s_client_example.py
```

### 使用範例

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

---

## ☸️ Kubernetes 集群環境

### 1. 配置 RBAC 權限

應用程序需要適當的 RBAC 權限才能訪問 Kubernetes API。

#### 使用 Helm 部署 (推薦)

```bash
# 安裝 (自動創建 ServiceAccount 和 RBAC)
helm install kubewizard ./helm

# 或使用自定義 values
helm install kubewizard ./helm \
  --set rbac.create=true \
  --set serviceAccount.create=true
```

#### 手動配置 RBAC

如果不使用 Helm,可以手動創建:

```yaml
# serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: kubewizard
  namespace: default

---
# clusterrole.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: kubewizard-role
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "namespaces", "nodes"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets"]
    verbs: ["get", "list", "watch"]

---
# clusterrolebinding.yaml
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

應用配置:

```bash
kubectl apply -f serviceaccount.yaml
kubectl apply -f clusterrole.yaml
kubectl apply -f clusterrolebinding.yaml
```

### 2. 配置 Deployment

在 Deployment 中指定 ServiceAccount:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kubewizard
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kubewizard
  template:
    metadata:
      labels:
        app: kubewizard
    spec:
      serviceAccountName: kubewizard  # 重要!
      containers:
      - name: kubewizard
        image: kubewizard:latest
        ports:
        - containerPort: 8000
```

### 3. 驗證配置

部署後驗證:

```bash
# 檢查 Pod 是否運行
kubectl get pods -l app=kubewizard

# 檢查 Pod 日誌
kubectl logs -l app=kubewizard

# 進入 Pod 驗證
kubectl exec -it <pod-name> -- python examples/k8s_client_example.py
```

---

## 🐳 Docker 容器環境

### 本地 Docker 測試

#### 1. 構建鏡像

```bash
docker build -t kubewizard:latest .
```

#### 2. 使用本地 kubeconfig 運行

```bash
# Linux/macOS
docker run -it --rm \
  -v ~/.kube/config:/root/.kube/config:ro \
  -e KUBECONFIG=/root/.kube/config \
  kubewizard:latest python examples/k8s_client_example.py

# Windows PowerShell
docker run -it --rm `
  -v ${HOME}\.kube\config:/root/.kube/config:ro `
  -e KUBECONFIG=/root/.kube/config `
  kubewizard:latest python examples/k8s_client_example.py
```

#### 3. 使用 docker-compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  kubewizard:
    build: .
    volumes:
      - ~/.kube/config:/root/.kube/config:ro
    environment:
      - KUBECONFIG=/root/.kube/config
    command: python examples/k8s_client_example.py
```

運行:

```bash
docker-compose up
```

---

## 🔄 配置優先級

K8sConfigManager 會按以下順序嘗試載入配置:

1. **In-Cluster 配置** (最高優先級)
   - 路徑: `/var/run/secrets/kubernetes.io/serviceaccount/`
   - 條件: 檢測到 Pod 環境變數

2. **指定的 kubeconfig 路徑**
   - 通過 `K8sConfigManager(kubeconfig_path="/path/to/config")` 指定

3. **環境變數 KUBECONFIG**
   - 從 `os.environ['KUBECONFIG']` 讀取

4. **預設路徑** (最低優先級)
   - `~/.kube/config`

---

## 🔧 故障排除

### 問題 1: 無法連接到 Kubernetes API

**症狀:**
```
ConfigException: unable to load configuration
```

**解決方案:**

1. 檢查 kubeconfig 文件是否存在:
   ```bash
   ls ~/.kube/config
   ```

2. 驗證 kubectl 連接:
   ```bash
   kubectl cluster-info
   ```

3. 檢查環境變數:
   ```bash
   # Linux/macOS
   echo $KUBECONFIG
   
   # Windows PowerShell
   echo $env:KUBECONFIG
   ```

### 問題 2: 權限被拒絕 (Forbidden)

**症狀:**
```
Forbidden: User "system:serviceaccount:default:kubewizard" cannot list pods
```

**解決方案:**

1. 檢查 ServiceAccount:
   ```bash
   kubectl get serviceaccount kubewizard
   ```

2. 檢查 ClusterRoleBinding:
   ```bash
   kubectl get clusterrolebinding kubewizard-binding
   ```

3. 驗證 RBAC 權限:
   ```bash
   kubectl auth can-i list pods --as=system:serviceaccount:default:kubewizard
   ```

4. 如果需要更多權限,更新 ClusterRole:
   ```bash
   kubectl edit clusterrole kubewizard-role
   ```

### 問題 3: 在容器中找不到 kubeconfig

**症狀:**
```
無法載入 kubeconfig 配置
```

**解決方案:**

確保在 Docker 運行時掛載了 kubeconfig:
```bash
docker run -v ~/.kube/config:/root/.kube/config:ro ...
```

### 問題 4: 日誌中沒有看到配置載入信息

**解決方案:**

設置日誌級別:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

---

## 📚 相關文檔

- [Kubernetes Python Client 官方文檔](https://github.com/kubernetes-client/python)
- [Kubernetes RBAC 授權](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [配置訪問多個集群](https://kubernetes.io/docs/tasks/access-application-cluster/configure-access-multiple-clusters/)

---

## 💡 最佳實踐

### 開發環境

1. ✅ 使用 `.env` 文件管理配置
2. ✅ 使用命名空間隔離測試資源
3. ✅ 定期更新 kubeconfig
4. ✅ 使用最小權限原則

### 生產環境

1. ✅ 使用 ServiceAccount 而非 kubeconfig
2. ✅ 實施最小權限 RBAC 策略
3. ✅ 啟用審計日誌
4. ✅ 定期輪換憑證
5. ✅ 使用 Pod Security Standards

### 安全建議

1. 🔒 不要在代碼中硬編碼憑證
2. 🔒 不要提交 kubeconfig 到版本控制
3. 🔒 限制 ServiceAccount 權限範圍
4. 🔒 使用 Secret 管理敏感信息
5. 🔒 定期審查 RBAC 權限

---

## 🤝 貢獻

如有問題或建議,請提交 Issue 或 Pull Request。
