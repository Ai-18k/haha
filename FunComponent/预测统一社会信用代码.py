import random
from datetime import datetime


def calculate_check_code(code_17):
    """
    计算统一社会信用代码的校验码（第18位）
    算法标准：GB 32100-2015 (MOD 31-2)
    """
    # 权重表（固定值）
    weights = [1, 3, 9, 27, 19, 26, 16, 17, 20, 29, 25, 13, 8, 24, 10, 30, 28]
    # 字符映射表（0-9, A-Z，去掉了I、O、S、V、Z）
    chars = "0123456789ABCDEFGHJKLMNPQRTUWXY"

    total = 0
    for i in range(17):
        c = code_17[i]
        if c.isdigit():
            value = int(c)
        else:
            value = ord(c) - 65 + 10  # A=10, B=11, ..., Y=34
        total += value * weights[i]

    check_code_index = (31 - (total % 31)) % 31
    return chars[check_code_index]


def generate_unified_social_credit_code(region_code="340104", date=None):
    """
    生成模拟的统一社会信用代码
    :param region_code: 行政区划码（6位数字，默认安徽省合肥市蜀山区340104）
    :param date: 成立日期（用于生成顺序码，默认当天）
    """
    # 1. 基础部分（固定+行政区划）
    base_code = "91" + region_code  # 第1-8位

    # 2. 生成时间相关顺序码（模拟MA+年份缩写+日期+随机）
    if date is None:
        # date = datetime.now()
        date = datetime(2023,5,1)
    year_code = date.strftime("%y")  # 年份后两位（如23）
    month_day_code = date.strftime("%m%d")  # 月日（如1010）
    random_code = ''.join(random.choices("ABCDEFGHJKLMNPQRTUWXY", k=3))  # 3位随机字母

    # 组合主体标识码（MA + 年份缩写 + 月日 + 随机码）
    org_code = f"MA{year_code}{month_day_code}{random_code}"

    # 3. 组合前17位并计算校验码
    code_17 = base_code + org_code
    check_code = calculate_check_code(code_17)

    return code_17 + check_code


# 示例：生成10个模拟代码（基于当前日期）
if __name__ == "__main__":
    print("模拟生成的统一社会信用代码（示例）：")
    for _ in range(10):
        code = generate_unified_social_credit_code()
        print(f"{code}  （校验位：{code[-1]}）")