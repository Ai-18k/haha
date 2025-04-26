import random
from pathlib import Path

class GenSocialId:
    # 登记管理部门代码和机构类别代码
    org_type = ["11", "12", "13", "19", "51", "52", "53", "59", "91", "92", "93", "Y1"]

    # 编码字符集（排除I/S/O/V/Z）
    social_basic = [
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        "A", "B", "C", "D", "E", "F", "G", "H", "J", "K",
        "L", "M", "N", "P", "Q", "R", "T", "U", "W", "X", "Y"
    ]

    # 权重表
    org_code_weight = [3, 7, 9, 10, 5, 8, 4, 2]
    social_id_weight = [1, 3, 9, 27, 19, 26, 16, 17, 20, 29, 25, 13, 8, 24, 10, 30, 28]

    # 字符到数值的映射
    social_id_index = {char: idx for idx, char in enumerate(social_basic)}

    @classmethod
    def get_social_code(cls):
        """生成统一社会信用代码"""
        code = ""
        code += cls.get_org_type()  # 前2位
        code += cls.get_area_code()  # 3-8位
        org_code = cls.get_org_code()  # 9-16位
        org_check = cls.get_org_check_code(org_code)  # 第17位
        code += org_code + org_check  # 9-17位
        code += cls.get_social_check_code(code)  # 第18位
        return code

    @classmethod
    def get_org_type(cls):
        """获取登记管理部门+机构类别代码"""
        return random.choice(cls.org_type)

    @classmethod
    def get_area_code(cls):
        """获取行政区划码(3-8位)"""
        area_codes = []
        try:
            # 使用 __file__ 获取当前脚本所在目录
            current_dir = Path(__file__).parent
            file_path = current_dir / "2014.txt"

            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    code = line.strip().split("\t")[0]
                    area_codes.append(code)
        except Exception as e:
            raise RuntimeError("加载行政区划数据失败") from e
        return random.choice(area_codes)

    @classmethod
    def get_org_code(cls):
        """生成组织机构代码(8位)"""
        return "".join(random.choices(cls.social_basic, k=8))

    @classmethod
    def get_org_check_code(cls, org_code):
        """计算组织机构代码校验位(第17位)"""
        total = 0
        for i, char in enumerate(org_code):
            total += int(char, 36) * cls.org_code_weight[i]
        check = 11 - (total % 11)
        if check == 11:
            return "0"
        elif check == 10:
            return "X"
        return str(check)

    @classmethod
    def get_social_check_code(cls, code_17):
        """计算统一信用代码校验位(第18位)"""
        total = 0
        for i, char in enumerate(code_17):
            total += cls.social_id_index[char] * cls.social_id_weight[i]
        check = 31 - (total % 31)
        if check == 31:
            return "0"
        elif check == 30:
            return "Y"
        return cls.social_basic[check]


if __name__ == "__main__":
    # while True:
        print(GenSocialId.get_social_code())