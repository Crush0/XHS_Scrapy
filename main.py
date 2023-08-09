import argparse
import os
import re
import urllib.request

from utils.XHSRequests import GetUserPosted, GetFeed


# 在此处default默认字段中填写你的cookie和要爬取的userId
def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cookie', type=str,
                        default='',
                        help='your cookie')
    parser.add_argument('--userId', type=str, default='',
                        help='the user_id you want scrapy')
    parser.add_argument('--withImage', default=True, help='scrapy image')
    parser.add_argument('--withVideo', default=True, help='scrapy video')
    parser.add_argument('--savePath', default='./output', help='save path')
    opt = parser.parse_args()
    return opt


def parseUserPosted(cookie, data, withImage, withVideo, savePath):
    has_more = data['has_more']
    cursor = data['cursor']
    notes = data['notes']
    for note in notes:
        noteType = note['type']
        if noteType == 'normal' and withImage:
            parseFeed(cookie, note, savePath)
        elif noteType == 'video' and withVideo:
            parseFeed(cookie, note, savePath)
    return has_more, cursor


def urlDownload(url, filename):
    # 检查文件夹是否存在，不存在则创建
    folder_path = os.path.dirname(filename)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 下载文件
    with open(filename, 'wb') as f:
        resp = urllib.request.urlopen(url)
        f.write(resp.read(resp.length))


index = 0


def parseFeed(cookie, note, savePath):
    global index
    noteId = note['note_id']
    feed = GetFeed(cookie, noteId)

    if feed['success']:
        data = feed['data']
        nickname = re.sub(r'[\\/:*?"<>|]', '', note['user']['nickname'])
        items = data['items']
        for item in items:
            noteCard = item['note_card']
            noteType = noteCard['type']
            title = re.sub(r'[\\/:*?"<>|]', '', noteCard['title'])
            index += 1
            if noteType == 'normal':
                imageList = noteCard['image_list']
                for image in imageList:
                    traceId = image['trace_id']
                    realSavePath = os.path.join(savePath, nickname, f'{index}-{title}')
                    print(f'正在下载图片 日志索引={index}\t日志标题={title}\t文件ID={traceId}')
                    urlDownload(f'https://sns-img-bd.xhscdn.com/{traceId}',
                                os.path.join(realSavePath, f'{traceId}.png'))
            else:
                video = noteCard['video']
                media = video['media']
                consumer = video['consumer']
                videoId = media['video_id']
                originVideoKey = consumer['origin_video_key']
                realSavePath = os.path.join(savePath, nickname, f'{index}-{title}')
                print(f'正在下载视频 日志索引={index}\t日志标题={title}\t文件ID={videoId}')
                urlDownload(f'https://sns-video-bd.xhscdn.com/{originVideoKey}',
                            os.path.join(realSavePath, f'{videoId}.mp4'))


def run(
        cookie='',
        userId='',
        withImage=True,
        withVideo=False,
        savePath='./output'
):
    cursor = ''
    resp = GetUserPosted(cookie, cursor, userId)
    if resp['success']:
        data = resp['data']
        has_more, cursor = parseUserPosted(cookie, data, withImage, withVideo, savePath)
        while has_more:
            resp = GetUserPosted(cookie, cursor, userId)
            if resp['success']:
                data = resp['data']
                has_more, cursor = parseUserPosted(cookie, data, withImage, withVideo, savePath)
            else:
                print(resp)
                raise Exception('爬取失败')
    else:
        print(resp)
        raise Exception('爬取失败')


def main(opt):
    run(**vars(opt))


def checkArgv(opt):
    if opt['cookie'] == '':
        print('请填写cookie')
        return False
    if opt['userId'] == '':
        print('请填写要爬取的userId')
        return False
    if not opt['withImage'] and not opt['withVideo']:
        print('至少爬取图片和视频其中之一')
        return False
    return True


if __name__ == '__main__':
    opt_ = parse_opt()
    if checkArgv(vars(opt_)):
        main(opt_)
