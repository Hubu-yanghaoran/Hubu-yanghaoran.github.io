# 搜索和时间模块

新增功能沿用 Fuwari 的 card-base、btn-regular、主题变量与响应式布局，不改封面和头像。

- `/search/`：检索笔记、排版资源和 PDF 文本，支持类型与主题筛选。Ctrl/⌘ + K 打开搜索。导航快速搜索显示前八条，提供完整结果入口。
- PDF：构建时用 Poppler 的 pdftotext 提取六份原文／译本，按物理页码建立索引；当前 99 页有文本。结果通过 pdf/page 参数进入对应文档和页码。页面不会从 URL 加载未登记的附件。没有文本层的扫描 PDF 需要额外 OCR，当前不索引。
- 侧栏时钟：固定 Asia/Shanghai，显示日期、星期与分钟，不显示秒。隐藏标签页时停止定时刷新，返回时校正，组件移除时清理计时器。
- `/timeline/`：从文章元数据生成按月排列的发布／更新记录，同日不重复，不生成虚构活动。

## 构建

需要 Node 24、项目锁定的 pnpm 9.14.4，以及系统命令 pdftotext（Ubuntu 包 poppler-utils）。GitHub Pages 工作流已包含安装步骤。

`pnpm build` 执行 Astro 构建和 scripts/build-search.mjs，生成网站与 PDF 共用的 Pagefind 索引。开发服务不生成搜索索引，应以生产构建测试搜索。PDF 附件仍从 public/content/ 登记的 note.json 读取，导入新文件后重新构建即可更新。

组件位置：FullSearch.svelte、widget/Clock.astro、pages/timeline.astro；PDF 跳页由 PdfReader.astro 与 public/assets/pdfjs/viewer.mjs 协作实现。
