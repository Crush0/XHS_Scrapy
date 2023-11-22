import argparse
import os
import re
import sys
import urllib.request

from utils.XHSRequests import GetUserPosted, GetFeed


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--userId', type=str, nargs='+', default=[],
                        help='the user_id you want scrapy')
    parser.add_argument('--withImage', default=True, help='should scrapy image')
    parser.add_argument('--withVideo', default=False, help='should scrapy video')
    parser.add_argument('--savePath', default='./output', help='save path')
    opt = parser.parse_args()
    cookie = open('./cookie.txt', 'r').read()
    if not cookie or cookie == '':
        raise Exception('Cookie is not set')
    opt.__setattr__('cookie', cookie)
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
    def _progress(block_num, block_size, total_size):
        percent = float(block_num * block_size) / float(total_size) * 100.0
        percent = 100.0 if percent > 100 else percent
        sys.stdout.write('\r>> Downloading %s %.1f%%' % (filename, percent))
        sys.stdout.flush()

    # 检查文件夹是否存在，不存在则创建
    folder_path = os.path.dirname(filename)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    urllib.request.urlretrieve(url, filename, _progress)
    print()


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
                index_ = 0
                for image in imageList:
                    imageInfo = image['info_list'][1]
                    realSavePath = os.path.join(savePath, nickname, f'{index}-{title}')
                    urlDownload(imageInfo['url'], os.path.join(realSavePath, f'{noteCard["note_id"]}_{index_}.png'))
                    index_ += 1
                    print(f'正在下载图片 日志索引={index}\t日志标题={title}\t文件ID={noteCard["note_id"]}_{index_}')
                    # urlDownload(f'https://sns-img-bd.xhscdn.com/{traceId}',
                    #             os.path.join(realSavePath, f'{traceId}.png'))
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
    else:
        print('Feed Err')


def run(
        cookie='',
        userId=None,
        withImage=True,
        withVideo=False,
        savePath='./output'
):
    if userId is None or userId == '':
        return
    cursor = ''
    for uid in userId:
        resp = GetUserPosted(cookie, cursor, uid)
        if resp['success']:
            data = resp['data']
            has_more, cursor = parseUserPosted(cookie, data, withImage, withVideo, savePath)
            while has_more:
                resp = GetUserPosted(cookie, cursor, uid)
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
    if len(opt['userId']) == 0:
        raise Exception('请填写要爬取的userId')
    if not opt['withImage'] and not opt['withVideo']:
        raise Exception('至少爬取图片和视频其中之一')
    return True


if __name__ == '__main__':
    opt_ = parse_opt()
    if checkArgv(vars(opt_)):
        main(opt_)
