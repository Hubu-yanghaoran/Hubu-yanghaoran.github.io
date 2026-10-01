# Yang Haoran 学术主页 · 第二版

参考 AcademicPages 的侧栏与内容分离思路，以及 al-folio 的克制排版。页面代码为本次独立编写，并非直接搬运上述主题；不包含它们的虚构学术示例。保留原版 Lumina 许可与下载资料。

## 比第一版多了什么

- 统一页眉、个人信息侧栏、首页、笔记库与模板库。
- 47 项模板目录可搜索、可按编译器分类；多引擎条目按首个匹配归类，仍可搜索其他引擎。
- site-config.js 管理个人信息；template-data.js 管理模板；样式和交互分别在 styles.css 与 app.js，内容不再写死在布局中。
- notes/ 中的 PDF 可通过 GitHub Actions 自动形成目录；首页同步显示最近笔记。没有凭空添加论文、学校或经历。
- site-config.js 的 publications 数组默认为空，成果栏目自动隐藏；有真实信息后再填写。

## 两种发布方式

### A. 保持目前的 main + /(root)，最少操作

上传 index.html、notes.html、templates.html、lumina-guide.html、styles.css、app.js、site-config.js、notes-data.js、template-data.js、lumina-preview.pdf 和 lumina-xelatex.zip 到仓库根目录。可同时上传 .nojekyll。保留你原来的仓库 README。

该方式不自动扫描笔记：上传 PDF 后，还需在 notes-data.js 的数组里添加标题、路径等。不要只上传 index.html；新版本需要多个文件。

示例（先上传 notes/algebra.pdf，再填写）：

```js
window.NOTES = [
  {title:"线性代数",description:"课程学习笔记",category:"数学",
   date:"2026-09-30",tags:["线性代数"],url:"notes/algebra.pdf"}
];
```

### B. 启用自动笔记目录

完整保留包内目录结构上传，包括 .github/workflows/pages.yml、scripts/build.py、notes/README.md、notes-metadata.json，以及上述网页文件。GitHub 网页批量上传对隐藏文件和目录处理不一，建议完整上传使用 Git 客户端；也可通过 Add file → Create new file，以 .github/workflows/pages.yml 为文件名创建工作流并粘贴原文。脚本同理。

在 Settings → Pages 将 Source 改为 GitHub Actions。这会替代你原来的“Deploy from a branch”。本地交付没有替你更改设置。若已有其他部署工作流，先合并或确认不要同时发布。

以后只需在 notes/ 上传公开 PDF 并提交，工作流自动生成目录并发布，默认以文件名为标题。文件上传必须保持 notes/ 路径；只上传根目录不会被扫描。当前仅索引扩展名为小写 .pdf 的文件。

注意：notes/ 中所有 PDF 都会公开发布，不要把私人文件放进来。工作流需要读取仓库及部署 Pages 的标准权限，但不需要你填写私人令牌。组织策略可能禁用工作流，遇到失败查看 Actions 日志。

## 自定义笔记信息

自动模式可编辑 notes-metadata.json，以路径为键：

```json
{
  "notes/algebra.pdf": {
    "title": "线性代数笔记",
    "description": "向量空间与线性映射",
    "category": "数学",
    "date": "2026-09-30",
    "tags": ["线性代数"]
  }
}
```

没有提供日期时不虚构上传日期。日期建议采用 YYYY-MM-DD。这个配置只有在自动构建时使用。

## 内容管理

个人名字、简介、GitHub 链接和主题标签改 site-config.js。模板名称、风格、引擎及来源改 template-data.js。请保持 JavaScript/JSON 标点格式正确。新增真实论文可填写 publications 数组，字段与笔记一致：title、description、date、url；它将在首页出现。

新栏目可复用已有页面外壳，增加导航和对应渲染函数。字体、间距、配色在 styles.css 集中管理。没有管理后台、登录上传或数据库，也不把任何 GitHub 密钥嵌入网页。

## 本地预览与升级安全

双击 index.html 可浏览默认页面（数据使用普通脚本加载，不要求本地服务器）。运行 python scripts/build.py 可生成 _site/，打开其 index.html 检查自动构建结果。_site 是发布产物，不要把它上传为仓库外层子目录。

旧版文件在此前交付包中保留。先备份线上改过的内容，再覆盖同名文件。旧有模板下载、PDF 预览及 lumina-guide.html 路径保持有效。部署后检查手机页面、搜索、下载与笔记链接；本地构建通过不代表 GitHub 已部署。

## 参考

- https://github.com/academicpages/academicpages.github.io
- https://github.com/alshedivat/al-folio

这是一份为当前主页独立制作的轻量静态实现，不包含上述主题的全部功能，且不是 al-folio 或 AcademicPages 的官方变体。模板目录环境信息沿用此前记录，未重新宣称 47 个模板全部编译通过。
