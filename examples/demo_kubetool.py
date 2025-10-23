"""
KubeTool 使用範例

展示如何使用 KubeTool 執行 kubectl 命令和直接使用 Kubernetes Python API
"""

import sys
import logging
import os
from pathlib import Path

# 添加專案根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def example_kubetool_basic():
    """範例 1: 使用 KubeTool 執行 kubectl 命令"""
    from tools.kubetool import KubeTool
    
    logger.info("=" * 70)
    logger.info("範例 1: 使用 KubeTool 執行 kubectl 命令")
    logger.info("=" * 70)
    
    tool = KubeTool()
    
    # 執行各種 kubectl 命令
    commands = [
        "kubectl version --client",
        "kubectl config current-context",
        "kubectl get nodes",
        "kubectl get namespaces",
    ]
    
    for cmd in commands:
        logger.info(f"\n執行命令: {cmd}")
        logger.info("-" * 70)
        result = tool.invoke({"commands": cmd})
        print(result)


def example_kubetool_with_approve():
    """範例 2: 使用需要審批的 KubeTool"""
    from tools.kubetool import KubeToolWithApprove
    
    logger.info("\n" + "=" * 70)
    logger.info("範例 2: 使用需要審批的 KubeTool")
    logger.info("=" * 70)
    
    tool = KubeToolWithApprove()
    
    # 這個命令會要求用戶確認
    logger.info("\n執行命令 (需要審批): kubectl get secrets -A")
    result = tool.invoke({"commands": "kubectl get secrets -A"})
    print(result)


def example_python_api():
    """範例 3: 直接使用 Kubernetes Python API"""
    from utils.k8s_config import get_k8s_config_manager
    
    logger.info("\n" + "=" * 70)
    logger.info("範例 3: 直接使用 Kubernetes Python API")
    logger.info("=" * 70)
    
    # 初始化配置管理器
    k8s_manager = get_k8s_config_manager()
    
    if not k8s_manager.load_config():
        logger.error("無法載入 Kubernetes 配置")
        return
    
    # 顯示環境信息
    if k8s_manager.is_in_cluster:
        logger.info("✓ 運行環境: Kubernetes 集群內")
    else:
        logger.info("✓ 運行環境: 本地開發環境")
    
    # 使用 CoreV1Api
    logger.info("\n--- 使用 CoreV1Api 列出命名空間 ---")
    v1 = k8s_manager.get_core_v1_api()
    namespaces = v1.list_namespace()
    
    for ns in namespaces.items[:5]:  # 只顯示前 5 個
        print(f"  - {ns.metadata.name}")
    
    # 使用 AppsV1Api
    logger.info("\n--- 使用 AppsV1Api 列出 Deployment ---")
    apps_v1 = k8s_manager.get_apps_v1_api()
    deployments = apps_v1.list_deployment_for_all_namespaces()
    
    for deploy in deployments.items[:5]:  # 只顯示前 5 個
        namespace = deploy.metadata.namespace
        name = deploy.metadata.name
        replicas = deploy.spec.replicas
        available = deploy.status.available_replicas or 0
        print(f"  - {namespace}/{name}: {available}/{replicas} replicas")


def example_combined():
    """範例 4: 結合使用 KubeTool 和 Python API"""
    from tools.kubetool import KubeTool
    from utils.k8s_config import get_k8s_config_manager
    
    logger.info("\n" + "=" * 70)
    logger.info("範例 4: 結合使用 KubeTool 和 Python API")
    logger.info("=" * 70)
    
    # 1. 使用 Python API 查詢 Pod
    logger.info("\n步驟 1: 使用 Python API 查詢異常的 Pod")
    k8s_manager = get_k8s_config_manager()
    k8s_manager.load_config()
    
    v1 = k8s_manager.get_core_v1_api()
    pods = v1.list_pod_for_all_namespaces()
    
    problem_pods = []
    for pod in pods.items:
        if pod.status.phase not in ["Running", "Succeeded"]:
            problem_pods.append({
                "namespace": pod.metadata.namespace,
                "name": pod.metadata.name,
                "status": pod.status.phase
            })
    
    if problem_pods:
        logger.info(f"找到 {len(problem_pods)} 個異常的 Pod:")
        for p in problem_pods[:3]:  # 只顯示前 3 個
            logger.info(f"  - {p['namespace']}/{p['name']}: {p['status']}")
        
        # 2. 使用 KubeTool 查看 Pod 詳情
        if problem_pods:
            pod = problem_pods[0]
            logger.info(f"\n步驟 2: 使用 kubectl describe 查看 Pod 詳情")
            tool = KubeTool()
            cmd = f"kubectl describe pod {pod['name']} -n {pod['namespace']}"
            result = tool.invoke({"commands": cmd})
            print(result[:500] + "..." if len(result) > 500 else result)
    else:
        logger.info("沒有找到異常的 Pod")


def main():
    """主函數"""
    logger.info("🚀 KubeTool 使用範例")
    
    # 檢查環境變數
    if 'KUBECONFIG' not in os.environ:
        logger.warning("⚠️  未設定 KUBECONFIG 環境變數")
        logger.warning("   在 PowerShell 中執行: $env:KUBECONFIG=\"$HOME\\.kube\\config\"")
        logger.warning("   在 Bash 中執行: export KUBECONFIG=~/.kube/config")
    
    try:
        # 執行範例 1: KubeTool 基本使用
        example_kubetool_basic()
        
        # 執行範例 2: KubeTool 審批模式
        # example_kubetool_with_approve()  # 取消註釋以測試審批功能
        
        # 執行範例 3: Python API
        example_python_api()
        
        # 執行範例 4: 結合使用
        example_combined()
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ 所有範例執行完成")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"\n❌ 執行錯誤: {e}", exc_info=True)
        logger.error("\n故障排除:")
        logger.error("  1. 確認 kubectl 已安裝: kubectl version --client")
        logger.error("  2. 確認可以連接集群: kubectl cluster-info")
        logger.error("  3. 檢查 KUBECONFIG: echo $env:KUBECONFIG (PowerShell)")
        logger.error("  4. 查看配置指南: docs/K8S_CONFIG_GUIDE.md")


if __name__ == "__main__":
    main()
