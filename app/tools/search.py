"""
联网搜索 Tool（模拟实现）
生产环境可替换为真实搜索引擎 API（如 Bing Search、SerpAPI）
"""


def web_search(query: str) -> str:
    """
    联网搜索农业知识

    参数:
        query: 用户查询文本

    返回:
        搜索结果字符串
    """
    # TODO: 接入真实搜索 API（如 Bing Search API、SerpAPI、百度搜索）
    # 当前为模拟数据
    return (
        f"关于「{query}」的搜索结果（模拟数据）：\n"
        f"1. 农业知识百科：{query}是农业生产中的重要概念...\n"
        f"2. 中国农业信息网：针对{query}的最新研究和实践...\n"
        f"3. 农技推广中心：{query}的标准操作规范...\n"
        f"\n温馨提示：当前为模拟数据，请接入真实搜索API获取准确信息。"
    )
