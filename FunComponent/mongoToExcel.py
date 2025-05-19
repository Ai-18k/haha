import pandas as pd
from pymongo import MongoClient
from typing import Dict, List


def connect_mongodb(host: str = '192.168.5.167', port: int = 27017) -> MongoClient:
    """连接MongoDB"""
    try:
        client = MongoClient(host, port)
        print("成功连接到MongoDB")
        return client
    except Exception as e:
        print(f"连接失败: {str(e)}")
        raise

def get_collection_counts(client, db_name: str, collections: List[str]) -> Dict[str, int]:
    """获取指定数据库中所有集合的文档数量"""
    db = client[db_name]
    counts = {}
    for coll_name in collections:
        try:
            counts[coll_name] = db[coll_name].estimated_document_count()
        except Exception as e:
            print(f"获取集合 {coll_name} 数量失败: {str(e)}")
            counts[coll_name] = 0
    return counts


def export_to_excel(data: Dict[str, Dict[str, int]], output_file: str = 'province_stats.xlsx'):
    """将统计数据导出到Excel"""
    # 转换为DataFrame，并重置索引
    df = pd.DataFrame.from_dict(data, orient='index').reset_index().rename(columns={'index': '省份'})

    # 使用ExcelWriter设置格式
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Collection Counts', index=False)

        workbook = writer.book
        worksheet = writer.sheets['Collection Counts']

        # 设置标题格式
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })

        # 直接应用标题格式（避免手动覆盖）
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # 设置自动列宽（遍历所有列）
        for i, col in enumerate(df.columns):
            max_len = max((
                df[col].astype(str).map(len).max(),  # 数据最大长度
                len(str(col))                        # 列标题长度
            )) + 4
            worksheet.set_column(i, i, max_len)

    print(f"统计数据已保存到 {output_file}")


def main():
    # 配置参数
    config = {
        "host": "192.168.5.167",
        "port": 27017,
        "provinces": [ "fujian",
                      "zhejiang",
                      "shanghai",
                      "shandong",
                      "guangdong",
                      "jiangsu",
                      "hubei",
                      "hebei",
                      "henan",
                      "beijing",
                      "tianjin",
                      "shanxi",
                      "neimenggu",
                      "liaoning",
                      "jilin",
                      "heilongjiang",
                      "anhui",
                      "jiangxi",
                      "hunan",
                      "guangxi",
                      "hainan",
                      "chongqing",
                      "sichuan",
                      "guizhou",
                      "yunnan",
                      "yunnan",
                      "xizang",
                      "sanxi",
                      "gansu",
                      "qinghai",
                      "ningxia",
                      "xinjiang",
                      "xianggang",
                       "taiwan"
                       ],
        "collections": [
            "company_id",
            "company",
            "company_qualification",
            "company_with",
            "sifa",
            "sorcomp",
            "电信许可",
            "行政许可",
            "资质证书",
            "zlxx",
            "软著著作权",
            "商标信息",
            "作品著作权",
            "sfaj",
            "被执行人",
            "裁判文书",
            "法院公告",
            "股权冻结",
            "经营异常",
            "限制消费",
            "行政处罚",
            "失信被执行人",
            "历史被执行人",
            "历史裁判文书",
            "历史法院公告",
            "历史股权冻结",
            "历史经营异常",
            "历史限制消费",
            "历史行政处罚",
            "历史失信被执行人",
        ],
        "output_file": "province_collection_counts.xlsx"
    }
    try:
        # 连接MongoDB
        client = connect_mongodb(config['host'], config['port'])

        # 统计每个省份的集合文档数量
        stats = {}
        for province in config['provinces']:
            print(f"正在处理省份: {province}")
            counts = get_collection_counts(client, province, config['collections'])
            stats[province] = counts

        # 导出到Excel
        export_to_excel(stats, config['output_file'])
    except Exception as e:
        print(f"执行过程中发生错误: {str(e)}")


if __name__ == "__main__":
    main()