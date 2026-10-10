"""
计算器 Tool
支持基本四则运算
"""

import re


def calculate(query: str) -> str:
    """
    从用户输入中提取数学表达式并计算

    参数:
        query: 用户查询文本（如"计算 3+5*2"）

    返回:
        计算结果字符串
    """
    # 提取数学表达式
    # 匹配数字、运算符、小数点、括号
    pattern = r'[\d\+\-\*\/\.\(\)\s]+'
    matches = re.findall(pattern, query)

    if not matches:
        return "未找到有效的数学表达式"

    # 取最长的匹配结果作为表达式
    expr = max(matches, key=len).strip()

    try:
        result = eval(expr, {"__builtins__": {}})
        return f"计算结果: {expr} = {result}"
    except Exception as e:
        return f"计算失败: {str(e)}"
