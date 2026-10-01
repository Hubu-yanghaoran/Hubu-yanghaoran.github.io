# Yang Haoran 个人知识库

这是原个人主页的渐进改进版，继续采用 Python 静态构建和 GitHub Pages。

## 本地预览

在完整改进包中双击上一级 start-preview.cmd。脚本构建网页并启动仅监听 127.0.0.1 的本地预览服务。浏览器打开 http://127.0.0.1:8765/；关闭终端窗口即可停止服务。

手动执行：

```text
python scripts/build.py
python scripts/check_links.py
python -m http.server 8765 --bind 127.0.0.1 --directory _site
```

实际网页位于 _site/。不要把 _site 当作源文件编辑，也不要直接发布项目根目录。

## 维护入口

| 文件 / 目录 | 用途 |
| --- | --- |
| site-config.json | 姓名、简介、学习方向、GitHub 与成果 |
| template-data.json | 第三方模板资源及归属信息 |
| templates/base.html | 所有新页面共用的导航、布局和页脚 |
| templates/home.html | 首页正文 |
| templates/catalog.html | 列表与检索界面 |
| templates/lumina.html | 模板适配说明 |
| scripts/layout.py | 静态列表、公共布局和首页生成 |
| scripts/content.py | 内容清单校验、附件收集和详情页 |
| scripts/markdown_reader.py | Markdown、图片、公式与目录 |
| styles.css / app.js / reader.js | 样式、检索交互和公式排版 |
| content/笔记ID/ | 唯一的新内容入口 |
| notes/ 与 projects/ | 旧内容兼容入口 |
| assets/katex/ | 固定版本的本地公式脚本、字体和许可 |
| vendor/ | 固定版本 Python Markdown 依赖及许可 |
| archive/ | 被替代的旧页面与重复配置，构建不发布 |

站点配置和资源数据会在构建时生成 site-config.js、template-data.js；笔记列表生成 notes-data.js。首页、分类列表及详情正文均生成实际 HTML，JavaScript 提供搜索、筛选与排序。

## 数学阅读

支持标题、链接、图片、引用、表格、嵌套列表、代码和公式。公式使用 $...$、$$...$$、\(...\)、\[...\]。目录锚点自动生成，重名标题自动区分。

Markdown 主文档中的相对图片会被校验并复制；支持 PNG/JPEG/WEBP/GIF。图片须位于同一笔记目录中。直接 HTML 作为文本转义；公式使用 KaTeX，trust=false。解析失败的公式保留原 TeX。

## 内容与更新

每篇笔记使用 content/稳定ID/note.json。目录就是稳定地址；修改标题时不要改目录。date 表示创建日期，updated 表示更新日期。标签、摘要、附件和使用说明写在 note.json 中，详情页自动生成。

上传器新增和更新均使用相同格式。旧 PDF 地址继续保留。

## GitHub Pages 升级

将 website/内的源码、模板、assets、vendor 和 .github 配置合并到现有仓库根目录，保留仓库已有 content/、notes/、projects/。示例笔记用于本地验收，是否保留由你决定。

不要上传 _site、__pycache__、本机 settings、草稿、checkout 或验收截图。本项目 .gitignore 已排除生成目录。

Actions 在 PR 上运行渲染测试、构建与内部链接检查；main 推送验证通过后部署。Actions 的远端执行仍需首次部署后验证。

## 测试

```text
python -m unittest discover -s scripts -p 'test_*.py' -v
python scripts/build.py
python scripts/check_links.py
```

Python 依赖已附带，可离线构建。数学资源也在本地，不使用外部 CDN。

## 当前视觉方向（第九批）

沿原网站的学术风格细化：白色背景、深蓝衬线姓名、蓝色链接、个人资料侧栏和顺序栏目。第五、六批的绿金风格与装饰首页已撤下。设计方向记录在 DESIGN.md 中；逐批验收文件和截图保留历史状态。

第八批整理公共 CSS、统一辅助文字为至少 13px（标签和短栏目标识除外）、加深文字对比度并增大手机链接区域。手机首页压缩重复身份展示，最近更新提前；矮桌面窗口的侧栏采用正常流，其他桌面窗口限制侧栏高度并允许滚动。

第九批对照 Lumina 示例，进一步细化衬线章节标题、小编号、留白和浅色重点区。Lumina 使用说明改为有目录、文件索引和清晰下载区的文稿页面；笔记标题区与正文宽度统一为最多 760px。代码块字号为 13px，长命令在代码区内滚动。

说明与笔记目录可展开或收起，桌面默认展开，820px 以下默认收起；没有 JavaScript 时保持展开，仍可直接浏览目录。样式、脚本及生成的内容数据附带版本地址，更新后不会继续复用同一地址的旧缓存。

正文首个 H1 与页面标题一致时，仅显示页面标题，同时保留原标题锚点和源文档。页面标题附有额外标记时，可在 note.json 填写 document_title 指明原文标题；其他标题不随意删改。

## 外部资源核查

resource-audit.json 保存 47 个资源入口的 HTTP 核查时间、状态及重定向地址。本轮均可访问。用 python scripts/audit_resources.py 可再次核查；需要网络，且不纳入离线构建或 CI 必须项。

HTTP 可达仅说明入口在核查时响应正常，不保证项目内容、编译环境或第三方下载包可用。目录中的编译环境仍应以项目说明为准，全部模板的实际编译测试尚未完成。

## 可选个人资料

site-config.json 中的 avatar、affiliation、location、email 为空时不显示相应资料；头像为空时采用原网站的 YHR 字母标识。

将自己的照片放入 assets/profile.jpg，并填写 "avatar": "assets/profile.jpg"，重新构建即可。建议使用接近正方形的照片，页面自动圆形裁切。

参考项目为用户提供的 Yixin 个人主页与 Academic Pages：

- https://github.com/Yixin0313/personal-homepage-template
- https://github.com/academicpages/academicpages.github.io

详细步骤见上一级第七批验收.md。当前设计不需要在线字体、外部背景图片或额外动画库。
