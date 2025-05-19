# 解析html格式

from lxml import etree
from datetime import datetime

# html=open("../version3.6-noRisk/1.html","r",encoding="utf-8").read()

def parasHTML(html,info):
	html = etree.HTML(html)
	try:
		company_name=str(html.xpath('//*[@id="company_web_top"]/div[3]/div[3]/div[1]/span/span/h1/text()')[0]).strip()
	except:
		company_name =None
	try:
		legal_name=str(html.xpath('//*[@id="_container_baseInfo"]/table/tbody/tr[1]/td[2]/div/div[1]/div[2]/div[1]/a/text()')[0]).strip()
	except:
		legal_name =None
	try:
		legal_telephone=str(html.xpath('//*[@id="company_web_top"]/div[3]/div[3]/div[3]/div[2]/div[1]/span/span[4]/text()')[0]).strip()
	except:
		legal_telephone =None
	if legal_telephone=='暂无信息':
		legal_telephone=None
	try:
		company_address=str(html.xpath('//*[@id="company_web_top"]/div[3]/div[3]/div[3]/div[3]/div[2]/span/div/div/div/text()')[0]).strip()
	except:
		company_address =None
	try:
		registered_address=str(html.xpath('//*[@id="_container_baseInfo"]/table/tbody/tr[10]/td[2]/span/span/span/text()')[0]).strip()
	except:
		registered_address =None
	try:
		staff_size=str(html.xpath('//*[@id="_container_baseInfo"]/table/tbody/tr[8]/td[2]/text()')[0]).strip()
	except:
		staff_size =None
	if staff_size=="-":
		staff_size=None
	create_by=1
	create_datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	update_by=None
	update_datetime=None
	is_deleted=1
	try:
		date_of_establishment=str(html.xpath('//*[@id="_container_baseInfo"]/table/tbody/tr[2]/td[2]/text()')[0]).strip()
	except:
		date_of_establishment =None
	try:
		registered_capital=str(html.xpath('//*[@id="_container_baseInfo"]/table/tbody/tr[3]/td[2]/div/text()')[0]).strip()
	except:
		registered_capital =None
	try:
		contributed_capital=str(html.xpath('//*[@id="_container_baseInfo"]/table/tbody/tr[4]/td[2]/text()')[0]).strip()
	except:
		contributed_capital =None
	if contributed_capital=="-":
		contributed_capital=None
	try:
		business_scope=contributed_capital=str(html.xpath('//*[@id="_container_baseInfo"]/table/tbody/tr[config]/td[2]/span/text()')[0]).strip()
	except:
		business_scope =None
	try:
		registration_status=str(html.xpath('//*[@id="_container_baseInfo"]/table/tbody/tr[1]/td[4]/text()')[0]).strip()
	except:
		registration_status =None
	try:
		tyxydm=str(html.xpath('//*[@id="_container_baseInfo"]/table/tbody/tr[5]/td[2]/span/span/text()')[0]).strip()
	except:
		tyxydm =None
	try:
		gszch=str(html.xpath('//*[@id="_container_baseInfo"]/table/tbody/tr[4]/td[4]/text()')[0]).strip()
	except:
		gszch =None
	try:
		nsrsbh=str(html.xpath('//*[@id="_container_baseInfo"]/table/tbody/tr[5]/td[4]/span/span/text()')[0]).strip()
	except:
		nsrsbh =None
	try:
		zzjgdm=str(html.xpath('//*[@id="_container_baseInfo"]/table/tbody/tr[5]/td[6]/span/span/text()')[0]).strip()
	except:
		zzjgdm =None
	try:
		nsrzz=str(html.xpath('//*[@id="_container_baseInfo"]/table/tbody/tr[6]/td[4]/text()')[0]).strip()
	except:
		nsrzz =None
	if nsrzz=="-":
		nsrzz=None
	try:
		yyqx=str(html.xpath('//*[@id="_container_baseInfo"]/table/tbody/tr[6]/td[2]/span/text()')[0]).strip()
	except:
		yyqx =None
	try:
		company_type=str(html.xpath('//*[@id="_container_baseInfo"]/table/tbody/tr[7]/td[2]/text()')[0]).strip()
	except:
		company_type =None
	try:
		registration_authority=str(html.xpath('//*[@id="_container_baseInfo"]/table/tbody/tr[8]/td[4]/text()')[0]).strip()
	except:
		registration_authority =None
	try:
		nameLevel2 = str(html.xpath('//*[@id="_container_baseInfo"]/table/tbody/tr[7]/td[4]/text()')[0]).strip()
	except:
		nameLevel2 =None
	try:
		short_name = str(html.xpath('//*[@id="company_web_top"]/div[3]/div[1]/div[1]/div[1]/span/text()')[0]).strip()
	except:
		short_name =None

	return {
		"shortName":short_name,
			"companyName":company_name,
			"legalName":legal_name,
			"legalTelephone":legal_telephone,
			"companyAddress":company_address,
			"create_datetime":create_datetime,
			"registeredAddress":registered_address,
			"companyPhone":None,
			"staffSize":staff_size,
			"dateOfEstablishment": date_of_establishment,
			"registeredCapital": registered_capital,
			"contributedCapital":contributed_capital,
			"businessScope":business_scope,
			"registrationStatus":registration_status,
			"tyxydm":tyxydm,
			"gszch":gszch,
			"nsrsbh":nsrsbh,
			"zzjgdm":zzjgdm,
			"shzzlx":None,
			"nsrzz":nsrzz,
			"yyqx":yyqx,
			"companyType":company_type,
			"registrationAuthority":registration_authority,
			'nameLevel2':nameLevel2,
			'nameLevel1':None,
			"provincialScope": None,
			"city": info['city'],
			"areaCode": info['areaCode'],
			"oldCompanyNameList": None,
			"dataSource":1
		}


# print(parasHTML(html,5345234))

