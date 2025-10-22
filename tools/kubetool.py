from typing import Optional, Type, Any, Callable
import os

from pydantic import Field, BaseModel
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_community.tools.shell.tool import ShellTool
import langchain_experimental 

from utils.console import confirm

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
    name: str = "KubeTool"
    """工具名稱"""

    description: str = "在 Kubernetes 集群上執行 k8s 相關命令（kubectl、helm）的工具。輸入是要執行的字串命令。"
    """工具描述"""

    args_schema: Type[BaseModel] = KubeInput

    def __init__(self, **kwargs):
        """使用適當的環境變數初始化 KubeTool"""
        super().__init__(**kwargs)
        # 確保從環境變數設定 KUBECONFIG
        if 'KUBECONFIG' in os.environ:
            kubeconfig = os.environ['KUBECONFIG']
            # 展開路徑中的環境變數
            kubeconfig = os.path.expandvars(kubeconfig)
            # 展開用戶主目錄
            kubeconfig = os.path.expanduser(kubeconfig)
            os.environ['KUBECONFIG'] = kubeconfig

    def _run(
        self,
        commands: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """執行命令並返回最終輸出"""
        commands = self._parse_commands(commands)
        return super()._run(commands)

    def _parse_commands(self, commands: str) -> str:
        """解析命令"""
        return commands.strip().strip('"`')

class KubeToolWithApprove(KubeTool):
    """執行 k8s 相關命令並檢查是否需要審批的工具"""

    name: str = "KubeToolWithApprove"
    """工具名稱"""

    approve: Callable[[Any], bool] = _default_approve

    description: str = "執行 k8s 相關命令並進行審批檢查的工具，如果命令會修改資源（delete、patch、create、update 等）或查看憑證資訊（secret）則需要審批。參數：字串類型，命令的原始字串。"
    """工具描述"""

    args_schema: Type[BaseModel] = KubeInput

    def _run(
        self,
        commands: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """執行命令並返回最終輸出"""
        if not self.approve(commands):
            return "命令執行已被用戶中止，未獲批准。"

        return super()._run(commands)
