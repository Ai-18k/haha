#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :detailparam.py
# @Time      :2024/11/19 18:25
# @Author    : 18k
import re
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Project root:", PROJECT_ROOT)
# 将项目根目录添加到Python路径
sys.path.append(PROJECT_ROOT)

from datetime import datetime
from loguru import logger

def getdata(data):
        item_info = dict()
        item_info["short_name"] = data["alias"] if data["alias"] else None
        hnlist = list()
        if "historyNames" in data:
            logger.info("历史名称:------->{}".format(data["historyNames"]))
            if "\n" in data["historyNames"]:
                hnlist.append(str(data["historyNames"]).split("\n").replace("-",""))
            else:
                hnlist.append(str(data["historyNames"]).replace("-",""))
        else:
            hnlist = list()
        item_info["historyNames"] = hnlist

        item_info["company_name"] = data["name"] if data["name"] else None

        item_info["legal_name"] = data["legalPersonName"] if data["legalPersonName"] else None

        if "phoneNum" in data:
            item_info["legal_telephone"] = data["phoneNum"] if data["phoneNum"] else None
        else:
            item_info["legal_telephone"] = None

        item_info["company_address"] = data["regLocation"] if data[
            "regLocation"] else None
        item_info["registered_address"] = data["regLocation"] if data["regLocation"] else None

        if "phoneList" in data:
            item_info["company_phone"] =",".join([item for item in data["phoneList"]])
        else:
            item_info["company_phone"] = None

        if "socialSecurityStaff_num" in data:
            item_info["staff_size"] = data["socialSecurityStaff_num"] if data[
                "socialSecurityStaff_num"] else None
        else:
            item_info["staff_size"] = None

        item_info["create_by"] = 1

        item_info["create_datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            if "estiblishTime" in data:
                if data["estiblishTime"]:
                    item_info["date_of_establishment"] = datetime.fromtimestamp(data["estiblishTime"] / 1000.0) if not isinstance(data["estiblishTime"],str) else data["estiblishTime"]
                else:
                    item_info["date_of_establishment"]=None
            else:
                item_info["date_of_establishment"] = None
        except:
            item_info["date_of_establishment"] = None

        item_info["registered_capital"] = data["regCapital"] if data[
            "regCapital"] else None

        try:
            match = re.findall(r"实缴资本(.*?)人民币", data["abstractsBaseInfo"])
            if match:
                # 获取匹配到的内容
                item_info["contributed_capital"] = match[0]
            else:
                item_info["contributed_capital"]=None
        except:
            item_info["contributed_capital"]=None

        if "businessScope" in data:
            item_info["business_scope"] = data["businessScope"] if data[
                "businessScope"] else None
        else:
            item_info["business_scope"] = None

        item_info["registration_status"] = data["regStatus"] if data[
            "regStatus"] else None
        if "creditCode" in data:
            item_info["tyxydm"] = data["creditCode"] if data[
                "creditCode"] else None
        else:
            item_info["tyxydm"] = None

        if "regNumber" in data:
            item_info["gszch"] = data["regNumber"] if data[
                "regNumber"] else None
        else:
            item_info["gszch"] = None

        item_info["nsrsbh"] = data["taxCode"] if data["taxCode"] else None

        item_info["zzjgdm"] = data["orgNumber"] if data["orgNumber"] else None

        item_info["yyqx"] = str(data["businessTerm"]).replace("-","") if data["businessTerm"] else None

        item_info["nameLevel2"] = data["categoryNameLv2"] if data["categoryNameLv2"] else None
        item_info["nameLevel1"] = data["categoryNameLv1"] if data["categoryNameLv1"] else None
        item_info["nameLevels"]={
                            "relationCompanyName": item_info["company_name"],
                            "relationIndustryName": item_info["nameLevel2"],
                            "relationIndustryPname": item_info["nameLevel1"],
                        }
        # nameLevel3=industryInfo["nameLevel3"]
        # 注册地址
        if "registerInstitute" in data:
            item_info["registration_authority"] = data["registerInstitute"] if data["registerInstitute"] else None
        else:
            item_info["registration_authority"] = None
        # 企业资质
        if "taxQualification" in data:
            item_info["nsrzz"] = data["taxQualification"] if data[
                "taxQualification"] else None
        else:
            item_info["nsrzz"] = None

        if data["companyType"]==3:
            if "orgType" in data:
                item_info["type"] = data["orgType"] if data["orgType"] else None
                item_info["company_type"] = None
            else:
                item_info["company_type"] = None
                item_info["type"]=None
        else:
            item_info["type"] = None
            if "orgType" in data:
                item_info["company_type"] = data["orgType"] if data["orgType"] else None
            else:
                item_info["company_type"] = None

        labelList=[]
        if "labelListV3" in data:
            if data["labelListV3"]:
                for tag in data["labelListV3"]:
                    if "profileTagNameOnPage" in tag:
                        profileTagNameOnPage=tag["profileTagNameOnPage"]
                        logger.success({"relationCompanyName": data["name"], "relationQualificationName":profileTagNameOnPage})
                        labelList.append({"relationCompanyName": data["name"], "relationQualificationName":profileTagNameOnPage})
                    else:
                        logger.success({"relationCompanyName": data["name"], "relationQualificationName": None})
                        labelList.append({"relationCompanyName": data["name"], "relationQualificationName": None})
            else:
                logger.success({"relationCompanyName": data["name"], "relationQualificationName": None})
                labelList.append({"relationCompanyName": data["name"], "relationQualificationName": None})
        else:
            logger.success({"relationCompanyName": data["name"], "relationQualificationName":None})
            labelList.append({"relationCompanyName": data["name"], "relationQualificationName": None})
        item_info["labelLists"]=labelList
        logger.info(item_info)
        return item_info

