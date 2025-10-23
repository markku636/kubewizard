"""
Kubernetes 配置管理工具

═══════════════════════════════════════════════════════════════════
模組目的：
═══════════════════════════════════════════════════════════════════
此模組提供 Kubernetes 配置的自動檢測和載入功能，
確保應用程式可以在不同環境下無縫運行。

支援的運行環境：
1. Kubernetes Pod 內部（生產環境）
   - 使用 ServiceAccount 自動掛載的憑證
   - 路徑：/var/run/secrets/kubernetes.io/serviceaccount/

2. 本地開發環境（開發/測試環境）
   - 使用 kubeconfig 文件
   - 預設路徑：~/.kube/config
   - 可通過 KUBECONFIG 環境變數指定

核心特性：
- 自動環境檢測（Pod vs 本地）
- 配置緩存（避免重複載入）
- 詳細的日誌輸出
- 優雅的錯誤處理
"""

import os
import logging
from typing import Optional
from kubernetes import client, config
from kubernetes.client import Configuration
from kubernetes.config.config_exception import ConfigException

logger = logging.getLogger(__name__)


class K8sConfigManager:
    """Kubernetes 配置管理器
    
    ═══════════════════════════════════════════════════════════════
    類別用途：
    ═══════════════════════════════════════════════════════════════
    這個類別是 KubeWizard 應用的核心配置組件，負責：
    
    1. 環境檢測
       - 自動判斷是否運行在 K8s Pod 內
       - 根據環境選擇適當的配置方式
    
    2. 配置載入
       - Pod 內：使用 ServiceAccount（load_incluster_config）
       - 本地：使用 kubeconfig 文件（load_kube_config）
    
    3. 狀態管理
       - 追蹤配置是否已載入
       - 記錄當前運行環境
    
    ═══════════════════════════════════════════════════════════════
    使用情境：
    ═══════════════════════════════════════════════════════════════
    1. 開發階段：
       - 開發者在本地機器上運行
       - 使用 ~/.kube/config 連接到測試集群
    
    2. 測試階段：
       - 在 CI/CD 流水線中運行測試
       - 可能在容器內或本地環境
    
    3. 生產環境：
       - 應用部署為 Kubernetes Pod
       - 自動使用 ServiceAccount 憑證
       - 不需要額外配置
    
    ═══════════════════════════════════════════════════════════════
    """
    
    def __init__(self, kubeconfig_path: Optional[str] = None):
        """初始化配置管理器
        
        初始化時不會立即載入配置，需要明確調用 load_config()。
        這樣設計可以延遲配置載入，直到真正需要時才執行。
        
        參數：
            kubeconfig_path: kubeconfig 文件的自訂路徑
                           - None: 使用預設路徑（~/.kube/config 或 KUBECONFIG 環境變數）
                           - 字串: 使用指定的檔案路徑
        
        內部狀態：
            self.kubeconfig_path: 保存 kubeconfig 路徑（可能為 None）
            self._config_loaded: 配置是否已載入（避免重複載入）
            self._is_in_cluster: 是否運行在 K8s Pod 內（用於日誌和診斷）
        """
        self.kubeconfig_path = kubeconfig_path
        self._config_loaded = False  # 初始狀態：未載入
        self._is_in_cluster = False  # 初始狀態：假設在本地
        
    def load_config(self) -> bool:
        """載入 Kubernetes 配置（自動檢測環境）
        
        這是配置管理器的核心方法，實現智能環境檢測。
        
        ═══════════════════════════════════════════════════════════
        執行流程：
        ═══════════════════════════════════════════════════════════
        1. 檢查配置緩存
           - 如果已載入 → 直接返回 True
           - 避免重複載入（提升效能）
        
        2. 嘗試載入集群內配置（優先）
           - 檢查 ServiceAccount 憑證是否存在
           - 路徑：/var/run/secrets/kubernetes.io/serviceaccount/
           - 如果成功 → 標記為 Pod 環境，返回 True
        
        3. 嘗試載入 kubeconfig 文件（備選）
           - 如果集群內配置失敗
           - 查找 kubeconfig 文件（環境變數或預設路徑）
           - 如果成功 → 標記為本地環境，返回 True
        
        4. 失敗處理
           - 如果兩種方式都失敗 → 記錄錯誤，返回 False
        
        ═══════════════════════════════════════════════════════════
        為什麼這樣設計？
        ═══════════════════════════════════════════════════════════
        - 優先嘗試 Pod 內配置：
          因為 Pod 環境不會有 kubeconfig 文件
          
        - 本地配置作為備選：
          本地開發環境不會有 ServiceAccount 憑證
        
        - 這種順序確保在任何環境都能正確運行
        
        返回：
            True: 配置載入成功
            False: 配置載入失敗
        """
        # ═══════════════════════════════════════════════════════════
        # 步驟 1: 檢查配置是否已載入（緩存機制）
        # ═══════════════════════════════════════════════════════════
        if self._config_loaded:
            logger.info("Kubernetes 配置已經載入")
            return True
            
        # ═══════════════════════════════════════════════════════════
        # 步驟 2: 嘗試載入集群內配置（Pod 環境）
        # ═══════════════════════════════════════════════════════════
        # 這會檢查 /var/run/secrets/kubernetes.io/serviceaccount/ 是否存在
        try:
            config.load_incluster_config()
            # 成功載入 Pod 內配置
            self._is_in_cluster = True
            self._config_loaded = True
            logger.info("✓ 成功載入集群內配置 (運行在 K8s Pod 中)")
            return True
        except ConfigException as e:
            # Pod 內配置不存在，這是正常情況（本地開發環境）
            logger.debug(f"無法載入集群內配置: {e}")
            
        # ═══════════════════════════════════════════════════════════
        # 步驟 3: 嘗試載入 kubeconfig 文件（本地環境）
        # ═══════════════════════════════════════════════════════════
        try:
            kubeconfig = self._get_kubeconfig_path()
            config.load_kube_config(config_file=kubeconfig)
            # 成功載入本地配置
            self._is_in_cluster = False
            self._config_loaded = True
            logger.info(f"✓ 成功載入 kubeconfig 配置: {kubeconfig}")
            return True
        except ConfigException as e:
            logger.error(f"✗ 無法載入 kubeconfig 配置: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ 載入配置時發生未預期的錯誤: {e}")
            return False
    
    def _get_kubeconfig_path(self) -> Optional[str]:
        """取得 kubeconfig 文件路徑
        
        Returns:
            str: kubeconfig 文件路徑
        """
        # 優先順序:
        # 1. 建構時指定的路徑
        # 2. 環境變數 KUBECONFIG
        # 3. 預設路徑 ~/.kube/config
        
        if self.kubeconfig_path:
            path = os.path.expanduser(os.path.expandvars(self.kubeconfig_path))
            logger.debug(f"使用指定的 kubeconfig 路徑: {path}")
            return path
            
        if 'KUBECONFIG' in os.environ:
            path = os.path.expanduser(os.path.expandvars(os.environ['KUBECONFIG']))
            logger.debug(f"使用環境變數 KUBECONFIG: {path}")
            return path
            
        default_path = os.path.expanduser("~/.kube/config")
        logger.debug(f"使用預設 kubeconfig 路徑: {default_path}")
        return default_path
    
    def get_api_client(self) -> client.ApiClient:
        """取得 Kubernetes API Client
        
        Returns:
            client.ApiClient: Kubernetes API 客戶端
            
        Raises:
            RuntimeError: 如果配置未載入
        """
        if not self._config_loaded:
            if not self.load_config():
                raise RuntimeError("無法載入 Kubernetes 配置")
        
        return client.ApiClient()
    
    def get_core_v1_api(self) -> client.CoreV1Api:
        """取得 CoreV1Api 客戶端
        
        Returns:
            client.CoreV1Api: K8s Core V1 API 客戶端
        """
        if not self._config_loaded:
            self.load_config()
        return client.CoreV1Api()
    
    def get_apps_v1_api(self) -> client.AppsV1Api:
        """取得 AppsV1Api 客戶端
        
        Returns:
            client.AppsV1Api: K8s Apps V1 API 客戶端
        """
        if not self._config_loaded:
            self.load_config()
        return client.AppsV1Api()
    
    def get_batch_v1_api(self) -> client.BatchV1Api:
        """取得 BatchV1Api 客戶端
        
        Returns:
            client.BatchV1Api: K8s Batch V1 API 客戶端
        """
        if not self._config_loaded:
            self.load_config()
        return client.BatchV1Api()
    
    def get_networking_v1_api(self) -> client.NetworkingV1Api:
        """取得 NetworkingV1Api 客戶端
        
        Returns:
            client.NetworkingV1Api: K8s Networking V1 API 客戶端
        """
        if not self._config_loaded:
            self.load_config()
        return client.NetworkingV1Api()
    
    @property
    def is_in_cluster(self) -> bool:
        """是否運行在集群內
        
        Returns:
            bool: True 表示運行在 K8s Pod 內
        """
        return self._is_in_cluster
    
    @property
    def is_configured(self) -> bool:
        """是否已配置
        
        Returns:
            bool: True 表示配置已成功載入
        """
        return self._config_loaded


# 全域實例 (單例模式)
_k8s_config_manager: Optional[K8sConfigManager] = None


def get_k8s_config_manager(kubeconfig_path: Optional[str] = None) -> K8sConfigManager:
    """取得全域 K8sConfigManager 實例
    
    Args:
        kubeconfig_path: kubeconfig 文件路徑
        
    Returns:
        K8sConfigManager: 配置管理器實例
    """
    global _k8s_config_manager
    
    if _k8s_config_manager is None:
        _k8s_config_manager = K8sConfigManager(kubeconfig_path)
        
    return _k8s_config_manager


def load_k8s_config(kubeconfig_path: Optional[str] = None) -> bool:
    """便捷函數: 載入 Kubernetes 配置
    
    Args:
        kubeconfig_path: kubeconfig 文件路徑
        
    Returns:
        bool: 是否成功載入
    """
    manager = get_k8s_config_manager(kubeconfig_path)
    return manager.load_config()
