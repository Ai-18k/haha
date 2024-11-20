#!/usr/bin/python
# -*- coding: utf8 -*-

import requests
import io
import sys
from loguru import logger
from lxml import etree

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') 


# headers = {
#     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
#     "accept-language": "zh-CN,zh;q=0.9",
#     "cache-control": "no-cache",
#     "dnt": "1.txt",
#     "pragma": "no-cache",
#     "priority": "u=0, i",
#     "referer": "https://www.google.co.jp/",
#     "sec-ch-prefers-color-scheme": "light",
#     "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
#     "sec-ch-ua-arch": "\"x86\"",
#     "sec-ch-ua-bitness": "\"64\"",
#     "sec-ch-ua-full-version": "\"128.0.6613.137\"",
#     "sec-ch-ua-full-version-list": "\"Chromium\";v=\"128.0.6613.137\", \"Not;A=Brand\";v=\"24.0.0.0\", \"Google Chrome\";v=\"128.0.6613.137\"",
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-model": "\"\"",
#     "sec-ch-ua-platform": "\"Windows\"",
#     "sec-ch-ua-platform-version": "\"10.0.0\"",
#     "sec-ch-ua-wow64": "?0",
#     "sec-fetch-dest": "document",
#     "sec-fetch-mode": "navigate",
#     "sec-fetch-site": "same-origin",
#     "sec-fetch-user": "?1.txt",
#     "upgrade-insecure-requests": "1.txt",
#     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
#     "x-client-data": "CKC1yQEIkrbJAQijtskBCKmdygEIjPzKAQiUocsBCJv+zAEI/JjNAQiFoM0BCKyezgEI5K/OAQi8uc4BGJ2xzgEYy7nOARiavM4B"
# }
# cookies = {
#     "NID": "517=q80dK2DAeJvG-v9jDjt7-bRvKwoMx74Dix_9-DfbnMiAbJraeGGHdB7gT_Z1H-z4IQKjlnNMHGIgTdkA0OqAQumrD_--hcBV1MRKaJjKg3cAivNG3p8_2vRD_mDPFC-ckbvTOhVeo__0sTX1ya8aEc1x2IVuy_NIrtyHSAMMbfkzUpvFO4l5"
# }
# url = "https://www.google.co.jp/search"
proxy={
    "http":"127.0.0.1.txt:7890",
    "https":"127.0.0.1.txt:7890"
}
# params = {
#     "q": "\"福州安博榕信息科技有限公司\"",
#     "sca_esv": "708ca891a389fdf3",
#     "sca_upv": "1.txt",
#     "biw": "446",
#     "bih": "607",
#     "ei": "t2biZuahI6q9vr0PwI_a6AM",
#     "ved": "0ahUKEwim2drewbyIAxWqnq8BHcCHFj0Q4dUDCA8",
#     "oq": "\"福州安博榕信息科技有限公司\"",
#     "gs_lp": "Egxnd3Mtd2l6LXNlcnAiKSLnpo_lt57lronljZrmppXkv6Hmga_np5HmioDmnInpmZDlhazlj7giSJY6UABYAHABeACQAQCYAQCgAQCqAQC4AQzIAQCYAgCgAgCYAwCIBgGSBwCgBwA",
#     "sclient": "gws-wiz-serp"
# }
# response = requests.get(url, headers=headers, cookies=cookies, params=params)

# print(response.text)
# print(response)



import requests
from bs4 import BeautifulSoup



def remove_html_and_css(text):

    soup = BeautifulSoup(text, 'lxml')
    for tag in soup.descendants:
        if hasattr(tag, 'attrs') and 'style' in tag.attrs:
            del tag['style']

    pure_text = ' '.join(soup.stripped_strings)

    return pure_text



def demo1(url):
    headers ={
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "DNT": "1.txt",
        "Pragma": "no-cache",
        "Referer": "https://www.google.co.jp/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1.txt",
        "Upgrade-Insecure-Requests": "1.txt",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\""
}
    response = requests.get(url, headers=headers,proxies=proxy)
    # html=etree.HTML(response.text)
    # print(html.xpath(".//span//text()"))
    if response.status_code==200:
        text=remove_html_and_css(response.text)
        print(text)


headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "dnt": "1.txt",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "referer": "https://www.google.co.jp/",
    "sec-ch-prefers-color-scheme": "light",
    "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    "sec-ch-ua-arch": "\"x86\"",
    "sec-ch-ua-bitness": "\"64\"",
    "sec-ch-ua-full-version": "\"128.0.6613.137\"",
    "sec-ch-ua-full-version-list": "\"Chromium\";v=\"128.0.6613.137\", \"Not;A=Brand\";v=\"24.0.0.0\", \"Google Chrome\";v=\"128.0.6613.137\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": "\"\"",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-ch-ua-platform-version": "\"10.0.0\"",
    "sec-ch-ua-wow64": "?0",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "upgrade-insecure-requests": "1.txt",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "x-client-data": "CKC1yQEIkrbJAQijtskBCKmdygEIjPzKAQiUocsBCJv+zAEI/JjNAQiFoM0BCKyezgEI5K/OAQi8uc4BGJ2xzgEYy7nOARiavM4B"
}
cookies = {
    "AEC": "AVYB7co9bULSnjyqQUd5wInIuk2l3Tck7axjMisLdMqCf14ZOvzEo6_tP2I",
    "HSID": "ABejwEko50CMozmjh",
    "SSID": "AJLZLS5ia_XY_5qwp",
    "APISID": "q2v-T9yJnLxzdUB-/A2seVnt8XPPoJPo7s",
    "SAPISID": "RJiWBVHh8EM-_idw/Abud-hldEDMh7hLJJ",
    "__Secure-1PAPISID": "RJiWBVHh8EM-_idw/Abud-hldEDMh7hLJJ",
    "__Secure-3PAPISID": "RJiWBVHh8EM-_idw/Abud-hldEDMh7hLJJ",
    "SID": "g.a000nwh0vVBQeUxu8P3Pl7wLrnBVtBG7aRFwPbkFlySTea21PLelkown2pLRBtFV_WMi62mYBQACgYKATISARISFQHGX2MiyMSchHsskrXG-4hv2QMxBxoVAUF8yKo77Sadkc1IcmhESMPJX_-T0076",
    "__Secure-1PSID": "g.a000nwh0vVBQeUxu8P3Pl7wLrnBVtBG7aRFwPbkFlySTea21PLelwK8V_VOQgD6Oa3sLGHXpKAACgYKAWASARISFQHGX2MiNK9GCGKBUO43yyxDXh_BhxoVAUF8yKqI0UqLqQmp74TwCeyLfm7U0076",
    "__Secure-3PSID": "g.a000nwh0vVBQeUxu8P3Pl7wLrnBVtBG7aRFwPbkFlySTea21PLelEsF8gVTOaZ-pauHa1QAmugACgYKATISARISFQHGX2MiOX34gLpAy1VJ3qzPvTtqghoVAUF8yKps4NWZUQrdQuaEPRjEvMm90076",
    "SEARCH_SAMESITE": "CgQIipwB",
    "NID": "517=EKk4ky384LoBMinRdxkaUfznHdETGeuCSiHNjJfdiWnWHf5G90NVjXNd9iTWLrzzzFPCm2m3LjOWrgkilXqO5v4pNEo2iWen_41qD6KmiLlSDYArzSHAfjLdA4zgi6MhDR1sBKCwRQydENlvsf3BZAh21Y16qRBFlQK7UVOcG9J5BdLJ3IxzIk_YncdOQJ_PP2VoBtnK29gtMDxGl2dbA4PA5CWqpU43kotg6IzjsKyqvSA5pKBA_JtYN7Ts-XmgcvWrpKEBRigxCuQLVNBIQ0XtDaFK9wQ4r8sHNgkWzaBEIlM0NUUqB8hk_PrKuWn2LYfqZj1_c1K-ASJex1c5x0iNhcLbxVq0uzUdsyAe_RS89bxz5hUiN6GGbZWiVx9fIKOcycao8FjC25eGcSB3Cq7Mvt0iwQ_RysX0FIl-_yU5ySOwm0o0MLOU4IaqsKsTpYz8mPH1QBJihYezcfr8aGId-nr4p_a_a3wSZ1KY6tiLsMBP7J0VrT3IVHqpGbrwTFG6uGug1poOP7gKDWM_pMkI1TZw9NRtSCZmTjxwEab1Z7XSWGJERMKkMvrPH3MxvFLKPyMeLKA-SiuRB5Ktj6V2ojug2vL8gBR7-k6AJIXXpQrCPRcCHVoRXSbgVfz9zNjJbM-CrwK7W-07y45QbuqW3EQilyTCLXyrhl7dUEr95nS-oHHjRsQYUDa2-d-50I0lrgeXQLB4jNPu4p5C77MTO6pjnKGd2QXzgKsE",
    "DV": "IxNOAhpmDCVbECBuCtWvdH13MihQHlkafDRcv1lcAwAAAFALlverd-v-HgAAAKBhEoxfPqk8DAAAAPob2FmvhbQoBwAAAA"
}
url = "https://www.google.co.jp/search"
params = {
    "q": "\"莆田市城厢区良达贸易有限公司\"",
    "sca_esv": "708ca891a389fdf3",
    "sca_upv": "1.txt",
    "biw": "887",
    "bih": "607",
    "ei": "-GbiZsiSDu6Qvr0Pqoz2OA",
    "ved": "0ahUKEwjI7sT9wbyIAxVuiK8BHSqGHQcQ4dUDCA8",
    "uact": "5",
    "oq": "\"莆田市城厢区良达贸易有限公司\"",
    "gs_lp": "Egxnd3Mtd2l6LXNlcnAiLCLojobnlLDluILln47ljqLljLroia_ovr7otLjmmJPmnInpmZDlhazlj7giMgsQABiABBiwAxiiBDILEAAYgAQYsAMYogRIjeAXUOTSF1jk0hdwBXgAkAEAmAEAoAEAqgEAuAEDyAEA-AEC-AEBmAIFoAJGmAMAiAYBkAYCkgcBNaAHAA",
    "sclient": "gws-wiz-serp"
}
response = requests.get(url, headers=headers, cookies=cookies, params=params,proxies=proxy)

# print(response.text)
# print(response)

html=etree.HTML(response.text)
borads=html.xpath('//div[@id="search"]/div/div/div')
# print(borads)
# try:
for borad in borads:
    try:
        title=borad.xpath(".//h3//text()")[0]
    except:
        title=borad.xpath(".//text()")
    try:
        href=borad.xpath(".//@href")[0]
    except:
        href=borad.xpath(".//a//@href")

    print(title)
    print(href)
    demo1(url)

# except:
#     pass



"""
 <div class="MjjYud"
<div class="MjjYud"


"""














