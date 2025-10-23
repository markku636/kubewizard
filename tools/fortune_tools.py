"""Fortune telling tools for the agent."""

from langchain.agents import tool
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.utilities import SerpAPIWrapper
import requests
import json
import os


# 元分居 API Key (需要从环境变量获取)
YUANFENJU_API_KEY = os.getenv("YUANFENJU_API_KEY", "ijJLuUjR0P72SnOfhoOHDTTga")


@tool
def search(query: str):
    """只有需要了解實時信息或不知道的事情的時候才會使用這個工具。"""
    serp = SerpAPIWrapper()
    result = serp.run(query)
    print("實時搜索結果:", result)
    return result


@tool
def bazi_cesuan(query: str):
    """只有做八字排盤的時候才會使用這個工具,需要輸入用戶姓名和出生年月日時，如果缺少用戶姓名和出生年月日時則不可用."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    url = "https://api.yuanfenju.com/index.php/v1/Bazi/cesuan"
    
    prompt = ChatPromptTemplate.from_template(
        """你是一個參數查詢助手，根據用戶輸入內容找出相關的參數並按json格式返回。JSON字段如下： 
        - "api_key":"ijJLuUjR0P72SnOfhoOHDTTga", 
        - "name":"姓名", 
        - "sex":"性別，0表示男，1表示女，根據姓名判斷", 
        - "type":"日歷類型，0農歷，1公里，默認1"，
        - "year":"出生年份 例：1998", 
        - "month":"出生月份 例 8", 
        - "day":"出生日期，例：8", 
        - "hours":"出生小時 例 14", 
        - "minute":"0"，
        如果沒有找到相關參數，則需要提醒用戶告訴你這些內容，只返回數據結構，不要有其他的評論，用戶輸入:{query}"""
    )
    
    parser = JsonOutputParser()
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("AI_MODEL", "gemini-2.0-flash"),
        temperature=0,
        google_api_key=os.getenv("AI_GOOGLE_API_KEY")
    )
    
    chain = prompt | llm | parser
    data = chain.invoke({"query": query})
    print("八字查詢結果:", data)
    
    result = requests.post(url, data=data)
    if result.status_code == 200:
        print("====返回數據=====")
        print(result.json())
        try:
            json_data = result.json()
            returnstring = "八字為:" + json_data["data"]["bazi_info"]["bazi"]
            return returnstring
        except Exception as e:
            return "八字查詢失敗,可能是你忘記詢問用戶姓名或者出生年月日時了。"
    else:
        return "技術錯誤，請告訴用戶稍後再試。"


@tool
def yaoyigua():
    """只有用戶想要占卜抽簽的時候才會使用這個工具。"""
    api_key = YUANFENJU_API_KEY
    url = "https://api.yuanfenju.com/index.php/v1/Zhanbu/yaogua"
    result = requests.post(url, data={"api_key": api_key})
    if result.status_code == 200:
        print("====返回數據=====")
        print(result.json())
        returnstring = json.loads(result.text)
        image = returnstring["data"]["image"]
        print("卦圖片:", image)
        return returnstring
    else:
        return "技術錯誤，請告訴用戶稍後再試。"


@tool
def jiemeng(query: str):
    """只有用戶想要解夢的時候才會使用這個工具,需要輸入用戶夢境的內容，如果缺少用戶夢境的內容則不可用。"""
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    api_key = YUANFENJU_API_KEY
    url = "https://api.yuanfenju.com/index.php/v1/Gongju/zhougong"
    
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("AI_MODEL", "gemini-2.0-flash"),
        temperature=0,
        google_api_key=os.getenv("AI_GOOGLE_API_KEY")
    )
    
    prompt = PromptTemplate.from_template("根據內容提取1個關鍵詞，只返回關鍵詞，內容為:{topic}")
    prompt_value = prompt.invoke({"topic": query})
    keyword = llm.invoke(prompt_value)
    print("提取的關鍵詞:", keyword)
    
    result = requests.post(url, data={"api_key": api_key, "title_zhougong": keyword})
    if result.status_code == 200:
        print("====返回數據=====")
        print(result.json())
        returnstring = json.loads(result.text)
        return returnstring
    else:
        return "技術錯誤，請告訴用戶稍後再試。"
