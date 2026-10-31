# Polaroid Camera Archive

**宝丽来历代相机目录：型号、外观、多角度参考与逐图来源。**

[在线图鉴](https://yuhua0987.github.io/polaroid-camera-archive/) · [English](README.en.md) · [浏览方式](#浏览) · [全部照片来源](docs/PHOTO_SOURCES.md) · [型号与视角清单](docs/COVERAGE.md) · [图片署名](docs/ATTRIBUTION.md) · [许可说明](NOTICE.md)

从 1948 年的卷片 Land 到 SX-70、600、Spectra、Go 与现代 i-Type，
这个项目把相机名称、地区铭牌、代际和外观参考整理成可搜索的静态图鉴。
由 [yuhua0987](https://github.com/yuhua0987) 维护，欢迎补图、勘误和改进查看器。

| 目录内容 | 数量 |
| --- | ---: |
| 历史系列分组 | 16 |
| 型号及命名版本条目 | 378 |
| 图片参考记录 | 1,211 |
| 参考图像，按内容去重 | 1,210 |
| 随公开仓库提供的开放许可图片 | **155** |
| 含开放图片的型号条目 | 60 |
| 有来源图片记录的型号条目 | 372 |
| 仍未找到对应照片的型号条目 | 6 |

资料快照：**2026-10-31**；公开版：**2026-11-01**，另补充 4 张 SX-70 开放许可照片。
378 是本目录的条目数，包含地区铭牌、代际与部分特别用途版本，不能等同于 378 种独立机身设计，也不是官方完整历史型号总数。

## 浏览

直接打开 **[在线图鉴](https://yuhua0987.github.io/polaroid-camera-archive/)**，无需下载或安装。

下载仓库 ZIP 并解压，双击根目录的 **`index.html`** 即可浏览。
数据、界面和 155 张开放图片都在本地，基础浏览无需联网或安装依赖。
其他图片保留来源链接，需要联网访问原始网页。

也可以运行一个仅本机可访问的静态服务器：

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

然后打开 <http://127.0.0.1:8000>。

图鉴支持：

- 按系列、型号编号或名称搜索。
- 按正面、斜前方、侧面、背面、斜后方及收合状态查看参考记录。
- 筛选“含开放图片”或“来源链接”，区分仓库内图像和外部参考。
- 按来源网站筛选，查看对应照片的原始页面和原图链接。
- 查看每张图的作者、尺寸、来源与许可；详情内用左右方向键切换。
- 查看缺图型号和仍待补齐、待核对的纯正 / 侧 / 背视角。

斜前方、斜后方和收合状态分别标注。照片数量不等于视角数量，各型号尚未全部配齐三视图。

## 范围

覆盖卷片 Land、撕拉片 Packfilm、80 系列、SX-70 折叠与盒式机、600、
Spectra / Image、Captiva / 500、i-Zone / Mio、Go、现代 i-Type、
大画幅专用机、证件照 / 专业系统、微距 / 科研系统、数码即印与 PIC-300。

SLR 680 / 690 归入 600 胶片系列；专业撕拉片 **600 / 600 SE** 单独归入 Packfilm，
避免与消费级 600 胶片相机混淆。

普通 35mm / APS、普通数码 / 运动相机、纯打印机、独立后背、第三方品牌和无限扩展的改皮 / 联名配色不计入。
仍可能遗漏冷门地区版、套装名称或特殊订制机。翻新、更换蒙皮和改装后背可能改变实物外观。

## 图片与许可

公开版保留完整来源索引，**不包含此前本地研究包里所有图片的副本**。
只有获得明确开放许可且保留署名的图片随仓库分发；官方产品图、商家图和评测图若未核实再分发授权，
仅作为来源链接收录，查看器不会自动热链加载它们。

| 内容 | 许可 |
| --- | --- |
| 原创查看器、构建工具与项目文档 | [MIT](LICENSE) |
| 原创目录编排与注释 | [CC BY-SA 4.0](data/LICENSE.md)，保留数据来源 |
| 开放图片与缩略图 | 各图原许可，见 [逐图署名](docs/ATTRIBUTION.md) |
| 其他来源记录 | 仅索引；不主张拥有原图的再分发权 |

**MIT 不覆盖第三方照片。** 缩略图进行了缩放与必要的白底合成；下载的图像响应保留原字节。
完整边界见 [NOTICE.md](NOTICE.md)，原许可元数据见 [media-manifest.json](data/media-manifest.json)。

### 其他照片在哪里

[全部照片来源索引](docs/PHOTO_SOURCES.md)覆盖 **64 个来源网站、1,211 条图片参考**，
包括其余 **1,056 条未复制到仓库的来源链接**。每条都列出型号、视角、作者或来源标注、
原始页面、原图地址和许可状态。可以按 Retrospekt、Polaroid Madness、FilmPhotography.eu
等网站查找，也可以在图鉴中选择“来源网站”后查看。

来源链接不等于图片副本已上传。尚未取得再分发许可的商家、评测与官方图像继续留在原网站；
许可核查记录见 [source-rights.json](data/source-rights.json)。

## 开发与构建

Python **3.10+**；构建和校验仅使用标准库，不需要 npm、数据库或 API 密钥。

```sh
python3 tools/validate.py
python3 tools/build.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory dist
```

修改 `web/` 后，更新随仓库提供的离线入口：

```sh
python3 tools/build.py --output .
```

| 路径 | 用途 |
| --- | --- |
| `web/` | HTML 模板、样式与查看器源码 |
| `data/catalog.json` | 型号、视角与来源索引 |
| `data/media-manifest.json` | 随仓库图片的作者、许可、修改说明与哈希 |
| `data/source-sites.json` | 全部来源网站的名称、记录数量与对应索引 |
| `docs/PHOTO_SOURCES.md` | 所有照片参考的来源网站总表 |
| `docs/sources/` | 按网站展开的逐条照片来源与原图链接 |
| `assets/media/` | 可再分发的图片响应 |
| `assets/thumbs/` | 遵循原图许可的预览图 |
| `docs/COVERAGE.md` | 逐型号参考记录和视角缺口 |
| `docs/ATTRIBUTION.md` | 每张开放图片的署名及许可 |
| `tools/` | 构建、目录校验与 Markdown 清单生成工具 |

数据字段见 [DATA_FORMAT.md](docs/DATA_FORMAT.md)。
静态站点可部署至 GitHub Pages；仓库提供可手动运行的 Pages 工作流，步骤见 [DEPLOYMENT.md](docs/DEPLOYMENT.md)。

## 贡献

欢迎提交可追溯的型号补充、铭牌纠正与多角度照片。
请在 issue / pull request 中给出型号编号、原始来源、作者与明确许可。
不要用相近型号填补缺图，也不要把一张斜前方照片标成完整三视图。
具体要求见 [CONTRIBUTING.md](CONTRIBUTING.md)。

本项目是独立爱好者资料库，与 Polaroid 官方无隶属关系。相机名称及商标归各权利人所有。
