"""
Kubernetes Python Client 使用範例

展示如何使用 K8sConfigManager 在不同環境下操作 Kubernetes API
"""

import logging
from utils.k8s_config import get_k8s_config_manager

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_list_pods():
    """範例: 列出所有命名空間的 Pod"""
    try:
        # 取得配置管理器並載入配置
        k8s_manager = get_k8s_config_manager()
        
        if not k8s_manager.load_config():
            logger.error("無法載入 Kubernetes 配置")
            return
        
        # 顯示運行環境
        if k8s_manager.is_in_cluster:
            logger.info("✓ 運行在 Kubernetes 集群內 (使用 ServiceAccount)")
        else:
            logger.info("✓ 運行在本地環境 (使用 kubeconfig)")
        
        # 取得 CoreV1Api 客戶端
        v1 = k8s_manager.get_core_v1_api()
        
        # 列出所有 Pod
        logger.info("\n=== 列出所有 Pod ===")
        pods = v1.list_pod_for_all_namespaces(watch=False)
        
        for pod in pods.items:
            namespace = pod.metadata.namespace
            name = pod.metadata.name
            status = pod.status.phase
            logger.info(f"{namespace:20s} {name:50s} {status}")
        
        logger.info(f"\n總共找到 {len(pods.items)} 個 Pod")
        
    except Exception as e:
        logger.error(f"錯誤: {e}", exc_info=True)


def example_get_namespaces():
    """範例: 列出所有命名空間"""
    try:
        k8s_manager = get_k8s_config_manager()
        k8s_manager.load_config()
        
        v1 = k8s_manager.get_core_v1_api()
        
        logger.info("\n=== 列出所有命名空間 ===")
        namespaces = v1.list_namespace(watch=False)
        
        for ns in namespaces.items:
            name = ns.metadata.name
            status = ns.status.phase
            created = ns.metadata.creation_timestamp
            logger.info(f"{name:30s} {status:10s} (創建於: {created})")
        
        logger.info(f"\n總共找到 {len(namespaces.items)} 個命名空間")
        
    except Exception as e:
        logger.error(f"錯誤: {e}", exc_info=True)


def example_get_deployments():
    """範例: 列出所有部署"""
    try:
        k8s_manager = get_k8s_config_manager()
        k8s_manager.load_config()
        
        apps_v1 = k8s_manager.get_apps_v1_api()
        
        logger.info("\n=== 列出所有 Deployment ===")
        deployments = apps_v1.list_deployment_for_all_namespaces(watch=False)
        
        for deploy in deployments.items:
            namespace = deploy.metadata.namespace
            name = deploy.metadata.name
            replicas = deploy.spec.replicas
            available = deploy.status.available_replicas or 0
            logger.info(f"{namespace:20s} {name:40s} {available}/{replicas} 可用")
        
        logger.info(f"\n總共找到 {len(deployments.items)} 個 Deployment")
        
    except Exception as e:
        logger.error(f"錯誤: {e}", exc_info=True)


def example_get_services():
    """範例: 列出所有服務"""
    try:
        k8s_manager = get_k8s_config_manager()
        k8s_manager.load_config()
        
        v1 = k8s_manager.get_core_v1_api()
        
        logger.info("\n=== 列出所有 Service ===")
        services = v1.list_service_for_all_namespaces(watch=False)
        
        for svc in services.items:
            namespace = svc.metadata.namespace
            name = svc.metadata.name
            svc_type = svc.spec.type
            cluster_ip = svc.spec.cluster_ip
            logger.info(f"{namespace:20s} {name:40s} {svc_type:15s} {cluster_ip}")
        
        logger.info(f"\n總共找到 {len(services.items)} 個 Service")
        
    except Exception as e:
        logger.error(f"錯誤: {e}", exc_info=True)


def example_get_nodes():
    """範例: 列出所有節點"""
    try:
        k8s_manager = get_k8s_config_manager()
        k8s_manager.load_config()
        
        v1 = k8s_manager.get_core_v1_api()
        
        logger.info("\n=== 列出所有 Node ===")
        nodes = v1.list_node(watch=False)
        
        for node in nodes.items:
            name = node.metadata.name
            
            # 取得節點狀態
            ready = "Unknown"
            for condition in node.status.conditions:
                if condition.type == "Ready":
                    ready = condition.status
                    break
            
            # 取得節點資訊
            kubelet_version = node.status.node_info.kubelet_version
            os_image = node.status.node_info.os_image
            
            logger.info(f"{name:40s} Ready={ready} v{kubelet_version} ({os_image})")
        
        logger.info(f"\n總共找到 {len(nodes.items)} 個 Node")
        
    except Exception as e:
        logger.error(f"錯誤: {e}", exc_info=True)


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("Kubernetes Python Client 範例")
    logger.info("=" * 80)
    
    # 執行各種範例
    example_list_pods()
    example_get_namespaces()
    example_get_deployments()
    example_get_services()
    example_get_nodes()
    
    logger.info("\n" + "=" * 80)
    logger.info("範例執行完成")
    logger.info("=" * 80)
