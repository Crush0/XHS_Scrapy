import re

import execjs


def GetXs(cookie, api, data):
    with open('./js/xhs_xs.js', 'r', encoding='utf-8') as f:
        jstext = f.read()
    ctx = execjs.compile(jstext)
    match = re.search(r'a1=([^;]+)', cookie)
    if match:
        a1 = match.group(1)
        result = ctx.call("get_xs", api, data, a1)
        return result
    else:
        raise Exception('Cookie 格式错误')
