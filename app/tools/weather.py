"""
天气查询 Tool（模拟实现）
生产环境可替换为真实天气 API（如和风天气、OpenWeatherMap）
"""


def get_weather(query: str) -> str:
    """
    查询天气信息

    参数:
        query: 用户查询文本（如"今天北京天气怎么样"）

    返回:
        天气信息字符串
    """
    # TODO: 接入真实天气 API
    # 当前为模拟数据
    city = "北京"
    for keyword in ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉"]:
        if keyword in query:
            city = keyword
            break

    return (
        f"{city}天气预报（模拟数据）：\n"
        f"今天：晴转多云，25°C ~ 32°C，风力3级\n"
        f"明天：多云，24°C ~ 30°C，风力2级\n"
        f"后天：小雨，22°C ~ 28°C，风力3级\n"
        f"\n温馨提示：当前为模拟数据，请接入真实天气API获取准确信息。"
    )
