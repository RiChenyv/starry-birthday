# 星河生日礼物

用姓名和庆祝日期生成一份离线生日网页。蛋糕和祝福在打开设备的本地时间当天零点解锁。

将三个文件放在同一目录，用 Python 3.8 或更新版本运行 `python generate.py`，按提示输入姓名和日期。也可直接传参。

```sh
python generate.py "小星" 2027-08-19
```

打开生成的 `dist/星河生日礼物.html` 即可查看或分享。用 `-o` 可指定其他输出路径。

```sh
python generate.py "小星" 2027-08-19 -o "dist/小星的生日礼物.html"
```

`template.html` 内嵌页面样式、脚本及 Three.js 的 MIT 许可。可在其中搜索 `letter-body` 编辑信件正文。
