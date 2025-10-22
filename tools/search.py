from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun, DuckDuckGoSearchResults
from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
import duckduckgo_search

def create_search_tool():
    """創建網路搜尋工具
    
    返回一個配置好的 DuckDuckGo 搜尋工具，用於搜尋 Kubernetes 相關資訊。
    
    Returns:
        DuckDuckGoSearchResults: 配置好的搜尋工具實例
    """
    return DuckDuckGoSearchResults(
        description="""
        在網路上搜尋主題相關資訊，以下是一些有用的 Kubernetes 資訊網站：
        - https://kubernetes.io/docs/: Kubernetes 官方文件
        - https://kuberentes.io: Kubernetes 社群網站
        - https://github.com/kubernetes/kubernetes: Kubernetes GitHub 儲存庫
        """,
        api_wrapper=DuckDuckGoSearchAPIWrapper(
            max_results=10,  # 最多返回 10 個結果
            time="y",  # 搜尋過去一年的內容
            backend="api",  # 使用 API 後端
            source="text"  # 返回文字內容
        )
    )

if __name__ == "__main__":
    tool = create_search_tool()
    tool.run("k8s latest version", verbose=True)
