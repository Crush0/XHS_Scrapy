import json

import requests

from utils.HeaderTemplate import GetHeaders
from utils.XSUtils import GetXs

BASEURL = 'https://edith.xiaohongshu.com'

session = requests.session()


def GetUserPosted(cookie, cursor, userId):
    api = f'/api/sns/web/v1/user_posted?num=30&cursor={cursor}&user_id={userId}&image_scenes='
    url = f'{BASEURL}{api}'
    encrypt = GetXs(cookie, api, '')
    header = GetHeaders(cookie, encrypt)
    resp = session.get(url, headers=header)
    return json.loads(resp.text)


def GetFeed(cookie, noteId):
    api = f'/api/sns/web/v1/feed'
    url = f'{BASEURL}{api}'
    data = {
        "source_note_id": noteId,
        "extra": {
            "need_body_topic": "1"
        },
        "image_scenes": [
            "CRD_PRV_WEBP",
            "CRD_WM_WEBP"
        ]
    }
    encrypt = GetXs(cookie, api, data)
    header = GetHeaders(cookie, encrypt)
    resp = session.post(url=url, headers=header, data=json.dumps(data, separators=(',', ':')))
    return json.loads(resp.text)
