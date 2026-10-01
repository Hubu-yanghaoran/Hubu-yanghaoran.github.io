# 统一内容规范

新内容放在 content/稳定ID/，每条笔记包含 note.json。ID 使用英文字母、数字、连字符和下划线；不要因标题变化重命名目录。

```json
{
  "title": "格的基与基本域",
  "description": "概念、例子与推导。",
  "category": "数学",
  "tags": ["格", "线性代数"],
  "date": "2026-10-01",
  "updated": "2026-10-01",
  "main": "chapters/main.md",
  "attachments": [
    {"file": "chapters/main.md", "label": "Markdown 原文"},
    {"file": "main.pdf", "label": "PDF 版本"}
  ],
  "author": "Yang Haoran"
}
```

main 必须对应一个已登记附件。附件路径相对笔记目录；附件支持 PDF、ZIP、TXT、MD、PNG、JPEG、WEBP、GIF。源码打包为 ZIP。构建只发布登记的附件及主 Markdown 实际引用的图片。

Markdown 会生成网页正文、公式与目录。示例目录：

```text
content/lattice-basis/
├── note.json
├── chapters/
│   ├── main.md
│   └── assets/格点.png
└── main.pdf
```

main.md 中使用 ![格点](assets/格点.png)，不需要把这张图片额外登记为下载附件。正文链接到其他本地文件时，该文件必须在 attachments 登记。

可选 engine、instructions、author、license、repository。instructions 和 tags 是字符串数组；repository 使用 HTTPS。无需自动为第三方资料套用许可。

旧 notes/ PDF、notes-metadata.json、projects/ 继续兼容。legacy_sources 可以登记被统一内容替代的旧条目，避免重复显示；旧附件直链仍保留。迁移前核对已有文件，不要覆盖仓库中的笔记数据。

草稿保存在本地上传工具的 drafts/，不提交到公开仓库。公开仓库里的文件是否出现在网页中，不影响其可公开读取。
