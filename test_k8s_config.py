"""
快速測試 Kubernetes 配置

驗證應用程序是否能正確連接到 Kubernetes 集群
"""

import sys
import logging
from kubernetes import client

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_k8s_connection():
    """測試 Kubernetes 連接"""
    try:
        # 導入配置管理器
        from utils.k8s_config import get_k8s_config_manager
        
        logger.info("=" * 70)
        logger.info("🔍 測試 Kubernetes 配置")
        logger.info("=" * 70)
        
        # 載入配置
        k8s_manager = get_k8s_config_manager()
        
        logger.info("\n📝 步驟 1: 載入配置...")
        if not k8s_manager.load_config():
            logger.error("❌ 無法載入 Kubernetes 配置")
            logger.error("\n請檢查:")
            logger.error("  1. 是否設定了 KUBECONFIG 環境變數")
            logger.error("  2. ~/.kube/config 文件是否存在")
            logger.error("  3. 是否在 Kubernetes Pod 中運行")
            return False
        
        # 顯示環境信息
        if k8s_manager.is_in_cluster:
            logger.info("✅ 配置載入成功!")
            logger.info("🏢 環境類型: Kubernetes 集群內 (使用 ServiceAccount)")
        else:
            logger.info("✅ 配置載入成功!")
            logger.info("💻 環境類型: 本地環境 (使用 kubeconfig)")
        
        # 測試 API 連接
        logger.info("\n📝 步驟 2: 測試 API 連接...")
        v1 = k8s_manager.get_core_v1_api()
        
        # 嘗試列出命名空間
        logger.info("   正在列出命名空間...")
        namespaces = v1.list_namespace(limit=5)
        
        logger.info(f"✅ API 連接成功! 找到 {len(namespaces.items)} 個命名空間:")
        for ns in namespaces.items[:5]:
            logger.info(f"   - {ns.metadata.name}")
        
        # 測試列出 Pod
        logger.info("\n📝 步驟 3: 測試列出 Pod...")
        logger.info("   正在列出 Pod (限制 5 個)...")
        pods = v1.list_pod_for_all_namespaces(limit=5)
        
        logger.info(f"✅ 成功列出 Pod! 找到 {len(pods.items)} 個 Pod:")
        for pod in pods.items[:5]:
            status = pod.status.phase
            logger.info(f"   - {pod.metadata.namespace}/{pod.metadata.name} ({status})")
        
        # 測試列出節點
        logger.info("\n📝 步驟 4: 測試列出節點...")
        try:
            nodes = v1.list_node()
            logger.info(f"✅ 成功列出節點! 找到 {len(nodes.items)} 個節點:")
            for node in nodes.items:
                version = node.status.node_info.kubelet_version
                logger.info(f"   - {node.metadata.name} (Kubelet: {version})")
        except Exception as e:
            logger.warning(f"⚠️  無法列出節點: {e}")
            logger.warning("   這可能是權限問題,但不影響基本功能")
        
        # 總結
        logger.info("\n" + "=" * 70)
        logger.info("🎉 所有測試通過!")
        logger.info("=" * 70)
        logger.info("\n✅ Kubernetes 配置正確")
        logger.info("✅ API 連接正常")
        logger.info("✅ 可以開始使用 KubeWizard")
        logger.info("\n建議:")
        logger.info("  - 運行完整範例: python examples/k8s_client_example.py")
        logger.info("  - 查看配置指南: docs/K8S_CONFIG_GUIDE.md")
        logger.info("=" * 70)
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ 導入錯誤: {e}")
        logger.error("\n請安裝必要的依賴:")
        logger.error("  pip install -r requirements.txt")
        return False
        
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}", exc_info=True)
        logger.error("\n故障排除:")
        logger.error("  1. 檢查 kubectl 是否能正常工作: kubectl get nodes")
        logger.error("  2. 檢查 KUBECONFIG 環境變數: echo $KUBECONFIG")
        logger.error("  3. 查看詳細指南: docs/K8S_CONFIG_GUIDE.md")
        return False


if __name__ == "__main__":
    success = test_k8s_connection()
    sys.exit(0 if success else 1)
