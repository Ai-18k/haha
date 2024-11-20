# _*_ coding:UTF-8 _*

"""遍历表的字段"""
from pymongo import MongoClient

serv_client = MongoClient(host='139.9.70.234', port=12700, username="root", password="QuyHlxXhW2PSHTwT",authSource="admin")

# print(serv_client.list_database_names())

f_dbs=['company','fujian', 'guangdong', 'hubei', 'jiangsu', 'judicial', 'licence','property', 'shandong', 'shanghai','zhejiang']

# print(serv_client['fujian'].list_collection_names())
def findDB():
    for db1 in f_dbs:
        s_dbs=serv_client[db1].list_collection_names()
        for db2 in s_dbs:
            if db2=="company_id":
                """ company_id 去重 """
                db=serv_client[db1][db2]
                # print(db.find_one())

            elif db2=="电信许可":
                """ 电信许可 去重 """
                dx_db = serv_client[db1][db2]
                print(dx_db.find_one())

            elif db2=="软著著作权":
                """ 软著著作权 去重 """
                rz_db = serv_client[db1][db2]
                print(rz_db.find_one())


def PolyWeightRemov():
    cli=serv_client["fujian"]["2nf_add_company_id"]
    # Aggregation pipeline
    pipeline = [
        {
            '$group': {
                '_id': {'company': '$company'},  # Group by the 'company' field
                'duplicates': {'$addToSet': '$_id'},  # Collect all _id values into an array
                'count': {'$sum': 1}  # Count occurrences of each group
            }
        },
        {
            '$match': {
                'count': {'$gt': 1}  # Match groups with more than one occurrence (duplicates)
            }
        },
        {
            '$project': {
                'duplicates': {
                    '$slice': ['$duplicates', 1, {'$subtract': [{'$size': '$duplicates'}, 1]}]
                }
            }
        }
    ]
    # Execute the aggregation pipeline
    results = list(cli.aggregate(pipeline))

    # Remove the duplicates
    for doc in results:
        for duplicate_id in doc['duplicates']:
            cli.delete_one({'_id': duplicate_id})

    # Close the connection
    serv_client.close()

PolyWeightRemov()

