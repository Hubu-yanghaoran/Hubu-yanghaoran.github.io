# 统一笔记更新指南

现在新内容只用 content/ 和 note.json，不再要求区分单篇与项目。同一分类、同一列表、同一种详情页。单文件只有一个附件，项目有多个附件。

## 升级需要的文件

覆盖 scripts/build.py 和 scripts/projects.py，新增 scripts/content.py。原有运行 scripts/build.py 的 Actions 工作流无需修改；已有笔记数据不要覆盖。推荐同时上传此说明与 content/README.md。

## 统一目录

```text
content/
└── linear-algebra/
    ├── note.json
    ├── main.pdf
    └── source.zip
```

每个子目录是一条笔记，目录名用英文、数字、连字符或下划线。配置示例：

```json
{
  "title": "线性代数笔记",
  "description": "向量空间与线性映射。",
  "category": "数学",
  "date": "2026-10-01",
  "tags": ["线性代数"],
  "main": "main.pdf",
  "attachments": [
    {"file": "main.pdf", "label": "完整笔记 PDF"},
    {"file": "source.zip", "label": "配套源码 ZIP"}
  ],
  "engine": "XeLaTeX",
  "instructions": ["解压源码后使用 XeLaTeX 编译 main.tex。"]
}
```

只有单个 PDF 时删除 source.zip 那一条，并去掉与源码有关的说明；没有主文档时删除 main。main 必须对应 attachments 中一个文件。附件路径相对于该笔记目录，标题和日期按实际修改。

可选字段：author、license、repository（真实 HTTPS 链接）。可以只提供 repository，不上传附件。

系统只发布列出的附件，不把其他源码、临时文件自动暴露到主页。支持 PDF、ZIP、TXT、MD、PNG/JPG/WEBP 附件；MD 暂时是原始文件链接，不是自动渲染的文章。源码请打成 ZIP，不自动编译或打包。

每条笔记都生成 content/目录名/index.html。分类中点击标题进入同样的详情页，再阅读主文档、查看附件或使用说明。无需手工创建详情 HTML。

## 旧内容兼容

旧 notes/ PDF 和 notes-metadata.json 继续读取，不删除文件。它们也会生成相同风格的详情页；旧 PDF 直链继续保留。

旧 projects/ 暂时兼容，已有链接不失效。新内容优先统一放 content/。

从旧内容迁移时，可在 note.json 添加 legacy_sources，避免列表重复：

```json
"legacy_sources": ["notes/algebra.pdf"]
```

旧项目使用其原条目地址，例如 projects/algebra/index.html。这些字段用于标记被替代的旧条目，不自动删除旧文件。迁移前备份；不要同时添加两个配置登记同一内容。

## 上传步骤与边界

先创建 content/目录名/README.md 建目录，上传附件，再创建 note.json。提交后现有 Actions 自动生成列表与页面。配置中引用不存在的文件会导致构建失败，先上传文件再登记。

本更新统一了存储、配置和观看，尚未实现本机一键上传程序或自动选择主文档。当前仍可直接在 GitHub 上传；不要把界面演示当作真实上传工具。

公开仓库里的附件即使未发布，也可能被读取，请勿上传私人文件。已有手动 notes-data.js 不会被自动构建读取。此文档优先于旧文档中 notes/ 与 projects/ 分别作为新内容入口的说明。
