from langchain_community.tools.human.tool import HumanInputRun

from utils.console import ask


def human_console_input():
    """創建人工輸入工具
    
    返回一個 HumanInputRun 工具實例，用於在需要時請求人工協助。
    """
    return HumanInputRun(
        description="僅在需要時請求人工協助，盡量減少使用",
        input_func=lambda: ask(prompt="📝"),
    )
