from typing import Optional, Type, Any, Callable
import os
import logging

from pydantic import Field, BaseModel
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_community.tools.shell.tool import ShellTool
import langchain_experimental 

from utils.console import confirm
from utils.k8s_config import get_k8s_config_manager

logger = logging.getLogger(__name__)

def _default_approve(_input: str) -> bool:
    """預設的審批函數
    
    詢問用戶是否批准執行輸入的命令。
    """
    msg = "您是否批准執行以下命令？ "
    return confirm(msg, extra=_input)

class KubeInput(BaseModel):
    """Kubernetes 工具的參數模型"""

    commands: str = Field(
        ...,
        example="kubectl get pods",
        description="要執行的 kubectl/helm 相關命令",
    )
    """要執行的 Kubectl 命令"""

class KubeTool(ShellTool):
    """Kubernetes 工具 - 執行 kubectl/helm 命令
    
    這個工具繼承自 LangChain 的 ShellTool，可以：
    1. 執行任意 kubectl 命令（如 kubectl get pods）
    2. 執行 helm 命令（如 helm list）
    3. 自動適配 K8s 集群內和本地環境
    
    工作原理：
    - Agent 決定使用此工具時，會調用 tool.invoke({"commands": "kubectl ..."})
    - invoke() 內部調用 _run() 方法
    - _run() 清理命令後，透過 ShellTool 在系統 shell 中執行
    - 執行結果返回給 Agent
    """
    
    name: str = "KubeTool"
    """工具名稱 - Agent 用此名稱識別工具"""

    description: str = "在 Kubernetes 集群上執行 k8s 相關命令（kubectl、helm）的工具。輸入是要執行的字串命令。"
    """工具描述 - Agent 用此描述決定何時使用此工具"""

    args_schema: Type[BaseModel] = KubeInput
    """參數模式 - 定義此工具接受的輸入格式"""

    def __init__(self, **kwargs):
        """初始化 KubeTool
        
        初始化過程：
        1. 調用父類 ShellTool 的初始化
        2. 載入 Kubernetes 配置（自動判斷環境）
        3. 處理 KUBECONFIG 環境變數
        """
        # ═══════════════════════════════════════════════════════════════
        # 步驟 1: 初始化父類 ShellTool
        # ═══════════════════════════════════════════════════════════════
        super().__init__(**kwargs)
        
        # ═══════════════════════════════════════════════════════════════
        # 步驟 2: 載入 K8s 配置（用於 Python Kubernetes SDK）
        # ═══════════════════════════════════════════════════════════════
        # 這會自動檢測運行環境：
        # - Pod 內：使用 ServiceAccount (/var/run/secrets/kubernetes.io/serviceaccount/)
        # - 本地：使用 kubeconfig 文件 (~/.kube/config 或 KUBECONFIG 環境變數)
        try:
            k8s_manager = get_k8s_config_manager()
            if k8s_manager.load_config():
                if k8s_manager.is_in_cluster:
                    logger.info("KubeTool: 使用集群內配置 (Pod 環境)")
                else:
                    logger.info("KubeTool: 使用本地 kubeconfig 配置")
            else:
                logger.warning("KubeTool: 無法載入 K8s 配置,可能會影響某些功能")
        except Exception as e:
            logger.warning(f"KubeTool: 初始化 K8s 配置時發生錯誤: {e}")
        
        # ═══════════════════════════════════════════════════════════════
        # 步驟 3: 處理 KUBECONFIG 環境變數（用於 kubectl 命令）
        # ═══════════════════════════════════════════════════════════════
        # kubectl 命令需要 KUBECONFIG 環境變數來找到配置文件
        # 這裡將路徑展開為絕對路徑（例如 ~ 展開為實際的家目錄）
        if 'KUBECONFIG' in os.environ:
            kubeconfig = os.environ['KUBECONFIG']
            # 展開環境變數（如 $HOME 或 %USERPROFILE%）
            kubeconfig = os.path.expandvars(kubeconfig)
            # 展開用戶主目錄符號（~ 或 ~user）
            kubeconfig = os.path.expanduser(kubeconfig)
            # 更新環境變數為展開後的絕對路徑
            os.environ['KUBECONFIG'] = kubeconfig

    def _run(
        self,
        commands: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """執行 shell 命令
        
        這是工具的核心執行方法，被 invoke() 調用。
        
        執行流程：
        1. 解析並清理命令字串
        2. 調用父類 ShellTool._run() 在系統 shell 中執行命令
        3. 返回命令執行結果
        
        參數：
            commands: 要執行的命令字串（如 "kubectl get pods"）
            run_manager: LangChain 的回調管理器（用於追蹤執行）
            
        返回：
            命令執行的輸出結果（stdout）
        """
        # 清理命令格式
        commands = self._parse_commands(commands)
        # 執行命令（調用父類 ShellTool 的實現）
        return super()._run(commands)

    def _parse_commands(self, commands: str) -> str:
        """解析和清理命令字串
        
        清理動作：
        - 移除開頭和結尾的空白
        - 移除開頭和結尾的引號（" 或 `）
        
        這確保 Agent 生成的命令格式一致，避免執行錯誤。
        """
        return commands.strip().strip('"`')

class KubeToolWithApprove(KubeTool):
    """Kubernetes 工具（帶審批機制） - 危險命令需要人工確認
    
    這個工具繼承自 KubeTool，增加了安全審批機制：
    - 繼承所有 KubeTool 的功能（kubectl/helm 命令執行）
    - 在執行前檢查命令是否危險
    - 危險命令需要人工批准才能執行
    
    危險命令包括：
    - 修改資源：delete, patch, create, update, apply, replace
    - 查看敏感資料：secret（可能包含憑證、密碼等）
    
    工作流程：
    1. Agent 決定使用此工具
    2. invoke() → _run() → 檢查命令
    3. 如果是危險命令 → 要求人工確認
    4. 如果確認通過（或非危險命令）→ 執行命令
    5. 返回結果給 Agent
    """

    name: str = "KubeToolWithApprove"
    """工具名稱 - Agent 用此識別工具"""

    approve: Callable[[Any], bool] = _default_approve
    """審批函數 - 用於詢問人工是否允許執行危險命令"""

    description: str = "執行 k8s 相關命令並進行審批檢查的工具，如果命令會修改資源（delete、patch、create、update 等）或查看憑證資訊（secret）則需要審批。參數：字串類型，命令的原始字串。"
    """工具描述 - Agent 用此決定何時使用此工具"""

    args_schema: Type[BaseModel] = KubeInput
    """參數模式 - 定義輸入格式"""

    def _run(
        self,
        commands: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """執行命令（帶審批檢查）
        
        這是帶審批機制的執行方法。
        
        執行流程：
        1. 檢查命令是否需要審批（由 approve 函數判斷）
        2. 如果需要審批：
           - 詢問用戶是否允許執行
           - 如果拒絕 → 返回中止訊息，不執行命令
           - 如果同意 → 繼續執行
        3. 執行命令（調用父類 KubeTool._run()）
        4. 返回執行結果
        
        安全機制：
        - 危險命令（delete, patch 等）必須經過人工確認
        - 未獲批准的命令會被攔截，不會實際執行
        - 確保關鍵操作有人工監督
        
        參數：
            commands: 要執行的命令字串
            run_manager: LangChain 回調管理器
            
        返回：
            命令執行結果（或拒絕訊息）
        """
        # ───────────────────────────────────────────────────────────────
        # 安全檢查：詢問用戶是否批准此命令
        # ───────────────────────────────────────────────────────────────
        if not self.approve(commands):
            # 用戶拒絕 → 返回中止訊息，不執行命令
            return "命令執行已被用戶中止，未獲批准。"

        # ───────────────────────────────────────────────────────────────
        # 執行命令：調用父類 KubeTool 的執行邏輯
        # ───────────────────────────────────────────────────────────────
        return super()._run(commands)
