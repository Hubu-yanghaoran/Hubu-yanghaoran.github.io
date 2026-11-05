# 网站样式与开源参考

本轮（2026-11-05）沿用 Python 静态构建与本地资源。参考以下开源项目的组织方式，自行编写本站的样式和偏好控件，没有引入其框架、主题运行时或远端字体。

| 项目 | 实际查阅的文件 | 本站采用的设计思路 |
| --- | --- | --- |
| [Quartz](https://github.com/jackyzha0/quartz) | v4 的 README、quartz/styles/base.scss、quartz/components/Explorer.tsx | 数字花园的信息分层、主题导航、保存用户选择。对应“数字花园”整体风格及主题筛选入口。 |
| [Hugo PaperMod](https://github.com/adityatelange/hugo-PaperMod) | master 的 README、assets/css/common/post-entry.css | 以文章为中心的简洁列表，明确区分标题、摘要与元数据。对应“列表”视图和克制的纸页排版。 |
| [al-folio](https://github.com/alshedivat/al-folio) | 当前 README；v0.14.0 的 _layouts/about.liquid | 学术身份、简介、最新记录与资源的层次。保留个人侧栏，强化主页阅读入口和分节标题。 |

“书架”是本站为 PDF 学习资料设计的原创呈现：标题、格式、标签和阅读入口形成书刊封面的层次，不将模拟封面误称为 PDF 首页缩略图。

## 可选择的样式

- 学术蓝：蓝白配色、清晰的分区和细边框，默认使用。
- 纸页：暖纸色、棕色链接、衬线标题、细直边框。
- 数字花园：绿色强调、无衬线标题、圆角表面。
- 笔记目录独立支持卡片、列表和书架。切换不改变内容，也不丢失搜索、分类和排序。
- 网页笔记支持无衬线／衬线正文与 16／18／20px 字号；PDF 保留原排版，使用自己的缩放控制。

偏好保存在浏览器本地 `yhr-appearance-v1`，不上传到服务器、不跨设备同步。笔记视图可通过 `notes.html?view=cards|list|shelf` 分享；有效 URL 参数优先于本地视图。无 JavaScript 时隐藏不能使用的控件，仍展示完整目录和文档链接；存储被禁用时，本页仍能切换样式并显示提示。

## 维护

外观使用 appearance.css 与 appearance.js；基础布局仍由 templates/base.html、scripts/layout.py 与 styles.css 提供。两份新增资源由 scripts/build.py 复制，URL 包含内容版本标记。保持 PDF.js、KaTeX 等上游资源及许可证独立；本站 viewer.css / viewer.mjs 负责 PDF 阅读区边框与工具栏的配色同步。
