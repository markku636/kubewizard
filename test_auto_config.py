"""
測試 Kubernetes 配置自動載入功能

驗證：
1. KubeTool 能自動載入配置
2. KubeAgent 能自動載入配置
3. Python API 能正常工作
"""

import sys
import logging
from pathlib import Path

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加專案根目錄到路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_k8s_config_manager():
    """測試配置管理器"""
    logger.info("=" * 70)
    logger.info("測試 1: K8s 配置管理器")
    logger.info("=" * 70)
    
    try:
        from utils.k8s_config import get_k8s_config_manager
        
        manager = get_k8s_config_manager()
        if manager.load_config():
            logger.info(f"✅ 配置載入成功")
            logger.info(f"   環境類型: {'集群內' if manager.is_in_cluster else '本地'}")
            
            # 測試 API 客戶端
            v1 = manager.get_core_v1_api()
            namespaces = v1.list_namespace(limit=1)
            logger.info(f"✅ API 連接正常 (找到 {len(namespaces.items)} 個命名空間)")
            return True
        else:
            logger.error("❌ 配置載入失敗")
            return False
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
        return False


def test_kubetool():
    """測試 KubeTool"""
    logger.info("\n" + "=" * 70)
    logger.info("測試 2: KubeTool")
    logger.info("=" * 70)
    
    try:
        from tools.kubetool import KubeTool
        
        tool = KubeTool()
        result = tool.invoke({"commands": "kubectl version --client"})
        
        if result and "Client Version" in result:
            logger.info("✅ KubeTool 執行成功")
            # 只顯示第一行
            first_line = result.strip().split('\n')[0]
            logger.info(f"   輸出: {first_line}")
            return True
        else:
            logger.error("❌ KubeTool 執行失敗")
            logger.error(f"   輸出: {result}")
            return False
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
        return False


def test_kube_agent():
    """測試 KubeAgent"""
    logger.info("\n" + "=" * 70)
    logger.info("測試 3: KubeAgent 初始化")
    logger.info("=" * 70)
    
    try:
        import os
        import dotenv
        
        # 載入環境變數
        dotenv.load_dotenv()
        
        # 檢查必要的環境變數
        if not os.getenv("AI_GOOGLE_API_KEY"):
            logger.warning("⚠️  未設定 AI_GOOGLE_API_KEY，跳過 KubeAgent 測試")
            return True
        
        from agents import KubeAgent
        
        agent = KubeAgent(user_id="test_user")
        logger.info("✅ KubeAgent 初始化成功")
        logger.info(f"   工具數量: {len(agent.tools)}")
        return True
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
        return False


def test_python_api():
    """測試 Python API 直接使用"""
    logger.info("\n" + "=" * 70)
    logger.info("測試 4: Kubernetes Python API")
    logger.info("=" * 70)
    
    try:
        from utils.k8s_config import get_k8s_config_manager
        
        manager = get_k8s_config_manager()
        manager.load_config()
        
        # 測試 CoreV1Api
        v1 = manager.get_core_v1_api()
        namespaces = v1.list_namespace(limit=3)
        logger.info(f"✅ CoreV1Api 正常 (列出 {len(namespaces.items)} 個命名空間)")
        
        # 測試 AppsV1Api
        apps_v1 = manager.get_apps_v1_api()
        deployments = apps_v1.list_deployment_for_all_namespaces(limit=3)
        logger.info(f"✅ AppsV1Api 正常 (列出 {len(deployments.items)} 個 Deployment)")
        
        return True
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
        return False


def main():
    """主測試函數"""
    logger.info("🧪 開始測試 Kubernetes 配置自動載入功能\n")
    
    results = {
        "配置管理器": test_k8s_config_manager(),
        "KubeTool": test_kubetool(),
        "KubeAgent": test_kube_agent(),
        "Python API": test_python_api(),
    }
    
    # 總結
    logger.info("\n" + "=" * 70)
    logger.info("📊 測試結果總結")
    logger.info("=" * 70)
    
    for name, result in results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        logger.info(f"{name:20s}: {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    logger.info("=" * 70)
    logger.info(f"總計: {passed}/{total} 測試通過")
    
    if passed == total:
        logger.info("🎉 所有測試通過！")
        return 0
    else:
        logger.error("⚠️  部分測試失敗")
        logger.error("\n故障排除:")
        logger.error("  1. 確認 kubectl 已安裝並可用")
        logger.error("  2. 確認 KUBECONFIG 環境變數已設定")
        logger.error("  3. 確認可以連接到 Kubernetes 集群")
        logger.error("  4. 查看詳細文檔: docs/K8S_CONFIG_GUIDE.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
