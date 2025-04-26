import requests


headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "dnt": "1",
    "downlink": "10",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.google.com/",
    "rtt": "150",
    "sec-ch-prefers-color-scheme": "dark",
    "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
    "sec-ch-ua-arch": "\"x86\"",
    "sec-ch-ua-bitness": "\"64\"",
    "sec-ch-ua-form-factors": "\"Desktop\"",
    "sec-ch-ua-full-version": "\"133.0.6943.98\"",
    "sec-ch-ua-full-version-list": "\"Not(A:Brand\";v=\"99.0.0.0\", \"Google Chrome\";v=\"133.0.6943.98\", \"Chromium\";v=\"133.0.6943.98\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": "\"\"",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-ch-ua-platform-version": "\"10.0.0\"",
    "sec-ch-ua-wow64": "?0",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "x-client-data": "CIi2yQEIpbbJAQipncoBCIn3ygEIlaHLAQiKo8sBCIWgzQEIn87OAQj3z84BCMnRzgEI/drOAQiu3s4BCJDfzgEIyOLOAQjJ4s4BGI/OzQE="
}
url = "https://www.google.com/complete/search"
params = {
    "q": "'威','夷','夏",
    "cp": "10",
    "client": "gws-wiz",
    "xssi": "t",
    "gs_pcrt": "undefined",
    "hl": "zh-CN",
    "authuser": "0",
    "psi": "yT61Z8rMJJCG0PEPyM6XqAs.1739931338926",
    "dpr": "1.2999999523162842",
    "pq": "'拿','大','加'"
}
response = requests.get(url, headers=headers, params=params,proxies={"http":"http://127.0.0.1:55491","https":"https://127.0.0.1:55491"})

print(response.text)
print(response)