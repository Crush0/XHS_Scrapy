# 小红书爬虫

# 安装依赖
```
    pip install PyExecJS
    pip install requests
```

# 使用方法
1. 打开要爬取的博主的主页，记录浏览器地址中的最后一串字符串，该字符串为`userId`
2. 打开开发者工具获得请求头中的`Cookie` 将其复制到`cookie.txt`中
3. 将`userId`填入`main.py`的`parse_opt()`中
4. 运行`main.py`

# 参数含义
|    参数名    |     参数含义     |   默认值    |
|:---------:|:------------:|:--------:|
|  userId   | 要爬取的用户userId |    -     |
| withImage |    是否爬取图片    |   True   |
| withVideo |    是否爬取视频    |   True   |
| savePath  |   文件保存根路径    | ./output |
