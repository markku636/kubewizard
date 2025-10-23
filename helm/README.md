# KubeWizard Helm Chart

這是 KubeWizard 的 Helm Chart，用於在 Kubernetes 集群中部署 AI 驅動的 Kubernetes 管理助手。

## 📋 前置需求

- Kubernetes 1.19+
- Helm 3.0+
- Google Gemini API Key

## 🚀 快速開始

### 1. 準備配置

創建 `values-custom.yaml` 文件：

```yaml
# 必填：Google Gemini API Key
secrets:
  AI_GOOGLE_API_KEY: "your-google-gemini-api-key-here"

# 可選：啟用 Ingress
ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: kubewizard.example.com
      paths:
        - path: /
          pathType: Prefix
```

### 2. 安裝 Chart

```bash
# 從本地目錄安裝
helm install kubewizard ./helm -f values-custom.yaml

# 或指定命名空間
helm install kubewizard ./helm -f values-custom.yaml --namespace kubewizard --create-namespace
```

### 3. 驗證部署

```bash
# 檢查 Pod 狀態
kubectl get pods -n kubewizard

# 查看服務
kubectl get svc -n kubewizard

# 查看日誌
kubectl logs -n kubewizard -l app.kubernetes.io/name=kubewizard -f
```

### 4. 存取應用

#### 使用 Port Forward（ClusterIP）

```bash
kubectl port-forward -n kubewizard svc/kubewizard 8000:8000
```

然後訪問：
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

#### 使用 NodePort

```yaml
# values-custom.yaml
service:
  type: NodePort
  nodePort: 30080
```

訪問：http://<node-ip>:30080

#### 使用 Ingress

```yaml
# values-custom.yaml
ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: kubewizard.example.com
      paths:
        - path: /
          pathType: Prefix
```

訪問：http://kubewizard.example.com

## ⚙️ 配置說明

### 基本配置

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `replicaCount` | Pod 副本數 | `1` |
| `image.repository` | 映像倉庫 | `kubewizard` |
| `image.tag` | 映像標籤 | Chart.appVersion |
| `image.pullPolicy` | 映像拉取策略 | `IfNotPresent` |

### RBAC 配置

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `serviceAccount.create` | 是否創建 ServiceAccount | `true` |
| `serviceAccount.name` | ServiceAccount 名稱 | 自動生成 |
| `rbac.create` | 是否創建 RBAC 資源 | `true` |

**RBAC 權限包含**：
- ✅ Pods, Services, Endpoints, Namespaces, Nodes, Events
- ✅ ConfigMaps, Secrets
- ✅ Deployments, ReplicaSets, StatefulSets, DaemonSets
- ✅ Jobs, CronJobs
- ✅ Ingresses, NetworkPolicies
- ✅ PersistentVolumes, PersistentVolumeClaims

這些權限允許 Pod 內的 kubectl 命令正常執行。

### Service 配置

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `service.type` | Service 類型 | `ClusterIP` |
| `service.port` | Service 端口 | `8000` |
| `service.nodePort` | NodePort（type=NodePort 時） | - |

### Ingress 配置

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `ingress.enabled` | 是否啟用 Ingress | `false` |
| `ingress.className` | Ingress Class | `nginx` |
| `ingress.hosts` | 主機配置 | `kubewizard.example.com` |
| `ingress.tls` | TLS 配置 | `[]` |

### 資源限制

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `resources.limits.cpu` | CPU 限制 | `1000m` |
| `resources.limits.memory` | 記憶體限制 | `1Gi` |
| `resources.requests.cpu` | CPU 請求 | `500m` |
| `resources.requests.memory` | 記憶體請求 | `512Mi` |

### Redis 配置

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `redis.enabled` | 是否部署 Redis | `true` |
| `redis.externalUrl` | 外部 Redis URL | - |
| `redis.persistence.enabled` | 是否啟用持久化 | `false` |
| `redis.persistence.size` | 持久化儲存大小 | `1Gi` |

### 環境變數配置

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `env.AI_MODEL` | AI 模型 | `gemini-1.5-flash-latest` |
| `env.AI_TEMPERATURE` | 溫度參數 | `0.7` |
| `env.DEBUG_LEVEL` | 調試級別 | `1` |
| `env.LOG_LEVEL` | 日誌級別 | `INFO` |
| `env.ENABLE_FORTUNE_TOOLS` | 啟用算命工具 | `false` |

### 密鑰配置

| 參數 | 說明 | 必填 |
|------|------|------|
| `secrets.AI_GOOGLE_API_KEY` | Google Gemini API Key | ✅ 是 |
| `secrets.YUANFENJU_API_KEY` | 元分橘 API Key | ❌ 否 |
| `secrets.SERPAPI_API_KEY` | SerpAPI Key | ❌ 否 |
| `secrets.LINE_CHANNEL_SECRET` | LINE Channel Secret | ❌ 否 |
| `secrets.LINE_CHANNEL_ACCESS_TOKEN` | LINE Access Token | ❌ 否 |

### 自動擴展配置

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `autoscaling.enabled` | 是否啟用 HPA | `false` |
| `autoscaling.minReplicas` | 最小副本數 | `1` |
| `autoscaling.maxReplicas` | 最大副本數 | `10` |
| `autoscaling.targetCPUUtilizationPercentage` | CPU 目標使用率 | `80` |

## 📝 配置範例

### 範例 1: 最小配置（僅 API Key）

```yaml
# values-minimal.yaml
secrets:
  AI_GOOGLE_API_KEY: "your-api-key-here"
```

```bash
helm install kubewizard ./helm -f values-minimal.yaml
```

### 範例 2: 使用外部 Redis

```yaml
# values-external-redis.yaml
secrets:
  AI_GOOGLE_API_KEY: "your-api-key-here"

redis:
  enabled: false
  externalUrl: "redis://my-redis.default.svc.cluster.local:6379/0"
```

### 範例 3: 啟用 Ingress 和 TLS

```yaml
# values-ingress.yaml
secrets:
  AI_GOOGLE_API_KEY: "your-api-key-here"

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: kubewizard.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: kubewizard-tls
      hosts:
        - kubewizard.example.com
```

### 範例 4: 啟用算命工具

```yaml
# values-fortune.yaml
secrets:
  AI_GOOGLE_API_KEY: "your-api-key-here"
  YUANFENJU_API_KEY: "your-yuanfenju-key"
  SERPAPI_API_KEY: "your-serpapi-key"

env:
  ENABLE_FORTUNE_TOOLS: "true"
```

### 範例 5: 生產環境配置

```yaml
# values-production.yaml
replicaCount: 3

secrets:
  AI_GOOGLE_API_KEY: "your-api-key-here"

resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 1000m
    memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

redis:
  enabled: true
  persistence:
    enabled: true
    size: 10Gi
    storageClass: "fast-ssd"
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 250m
      memory: 256Mi

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
  hosts:
    - host: kubewizard.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: kubewizard-tls
      hosts:
        - kubewizard.example.com

nodeSelector:
  workload: ai-applications

tolerations:
  - key: "ai-workload"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"
```

## 🔧 管理命令

### 升級 Release

```bash
# 升級到新版本
helm upgrade kubewizard ./helm -f values-custom.yaml

# 升級並重啟所有 Pod
helm upgrade kubewizard ./helm -f values-custom.yaml --recreate-pods
```

### 回滾 Release

```bash
# 查看歷史版本
helm history kubewizard

# 回滾到上一個版本
helm rollback kubewizard

# 回滾到指定版本
helm rollback kubewizard 2
```

### 查看配置

```bash
# 查看當前配置
helm get values kubewizard

# 查看所有配置（包含預設值）
helm get values kubewizard --all
```

### 測試配置

```bash
# 渲染模板但不安裝
helm template kubewizard ./helm -f values-custom.yaml

# 測試安裝（dry-run）
helm install kubewizard ./helm -f values-custom.yaml --dry-run --debug
```

### 卸載 Release

```bash
# 卸載但保留歷史
helm uninstall kubewizard

# 完全卸載（包含 PVC）
helm uninstall kubewizard
kubectl delete pvc -n kubewizard -l app.kubernetes.io/instance=kubewizard
```

## 🔍 故障排查

### 1. Pod 無法啟動

```bash
# 查看 Pod 狀態
kubectl get pods -n kubewizard

# 查看 Pod 詳情
kubectl describe pod -n kubewizard <pod-name>

# 查看日誌
kubectl logs -n kubewizard <pod-name>
```

常見問題：
- ❌ API Key 未配置或無效
- ❌ 映像拉取失敗
- ❌ 資源限制過低

### 2. 無法存取 Kubernetes API

```bash
# 檢查 ServiceAccount
kubectl get sa -n kubewizard

# 檢查 RBAC
kubectl get clusterrole kubewizard
kubectl get clusterrolebinding kubewizard

# 測試權限
kubectl auth can-i get pods --as=system:serviceaccount:kubewizard:kubewizard
```

### 3. Redis 連接失敗

```bash
# 檢查 Redis Pod
kubectl get pods -n kubewizard -l app.kubernetes.io/component=redis

# 測試 Redis 連接
kubectl exec -n kubewizard <kubewizard-pod> -- redis-cli -h kubewizard-redis ping
```

### 4. 查看完整日誌

```bash
# 實時查看日誌
kubectl logs -n kubewizard -l app.kubernetes.io/name=kubewizard -f --tail=100

# 查看前一個容器的日誌（如果重啟過）
kubectl logs -n kubewizard <pod-name> --previous
```

## 🔐 安全建議

1. **使用 Kubernetes Secret 管理敏感資訊**
   ```bash
   # 創建 Secret
   kubectl create secret generic kubewizard-secrets \
     --from-literal=AI_GOOGLE_API_KEY=your-key \
     -n kubewizard
   
   # 使用現有 Secret
   helm install kubewizard ./helm \
     --set existingSecret=kubewizard-secrets
   ```

2. **限制 RBAC 權限**
   - 根據實際需求調整 `rbac.rules`
   - 考慮使用 Role 而不是 ClusterRole

3. **啟用網路策略**
   ```yaml
   # 僅允許來自特定命名空間的流量
   networkPolicy:
     enabled: true
     ingress:
       - from:
         - namespaceSelector:
             matchLabels:
               name: frontend
   ```

4. **使用 TLS**
   - 配置 Ingress TLS
   - 使用 cert-manager 自動管理證書

## 📚 更多資源

- [KubeWizard GitHub](https://github.com/markku636/kubewizard)
- [Helm 文檔](https://helm.sh/docs/)
- [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License - 查看 LICENSE 文件了解詳情
