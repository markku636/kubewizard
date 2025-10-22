from typing import Any
from langchain_community.tools.requests.tool import RequestsGetTool
from langchain_community.utilities.requests import TextRequestsWrapper
from bs4 import BeautifulSoup
from html2text import HTML2Text

def get_parser() -> HTML2Text:
    """創建並配置 HTML 轉文字解析器
    
    返回一個配置好的 HTML2Text 解析器，忽略連結、圖片、強調和郵件連結。
    """
    parser: HTML2Text = HTML2Text()
    parser.ignore_links = True
    parser.ignore_images = True
    parser.ignore_emphasis = True
    parser.ignore_mailto_links = True
    return parser

class RequestsGet(RequestsGetTool):
    name: str = "RequestsGet"
    description: str = """通往互聯網的門戶。當您需要從網站獲取特定內容時使用此工具。
    輸入應該是一個 URL（例如 https://www.kubernetes.io/releases）。
    輸出將是 GET 請求的文字回應。
    """
    requests_wrapper: str = TextRequestsWrapper()
    allow_dangerous_requests: bool = True

    parser: HTML2Text = get_parser()

    def _run(self, url: str, **kwargs: Any) -> str:
        """執行 HTTP GET 請求並返回純文字內容
        
        Args:
            url: 要請求的網址
            
        Returns:
            網頁的純文字內容
        """
        url = url.strip().strip('"`')
        response = super()._run(url, **kwargs)
        soup = BeautifulSoup(response, 'html.parser')
        # 移除頁首、頁尾、腳本和樣式標籤
        for tag in soup(['header', 'footer', 'script', 'styple']):
            tag.decompose()
        data = self.parser.handle(soup.prettify())
        return data

if __name__ == "__main__":
    tool = RequestsGet(allow_dangerous_requests=True)
    print(tool.invoke("https://www.kubernetes.io/releases"))
