# Fuwari 原版迁移预览

原版来源：saicaca/fuwari，提交 6d39b0dec41282e7852e23e032998a5789abee28，代码许可见 LICENSE。用户已批准上线，本目录现为网站源码。

保留原版布局、组件、字体与交互。配置已替换为 Yang Haoran，语言为简体中文。通过 scripts/import-existing.py 从相邻旧网站导入五篇笔记、六份 PDF、一份 Markdown 和排版资源；原附件保持字节一致。原内容地址保留跳转至 /posts/ 对应页面。

PDF 页面新增 PdfReader.astro，支持原文／译文切换、独立打开、下载与连续阅读；自定义元素生命周期支持原版 Swup 页面切换。原模板默认的文章 CC 许可标识已关闭，避免给第三方论文错误授权。

原版附带的封面和头像用于本地预览。上游图片来源在“关于”页面保留，公开使用许可尚未确认，正式发布前应确认或替换。当前仓库自带的蓝色抽象封面与官方演示截图里的动漫封面不同。

## 本地命令

Node 24 与 pnpm 9.14.4 已验证。依赖按原版 pnpm-lock.yaml 安装。

```sh
cd /workspace/Hubu-yanghaoran.github.io
ASTRO_TELEMETRY_DISABLED=1 node_modules/.bin/astro check
ASTRO_TELEMETRY_DISABLED=1 node_modules/.bin/astro build
node_modules/.bin/pagefind --site dist
ASTRO_TELEMETRY_DISABLED=1 node_modules/.bin/astro preview --host 127.0.0.1
```

类型检查：0 errors、0 warnings，保留上游一项未使用变量 hint。构建生成 9 页，搜索索引含 6 页。内部链接校验通过 16 页、751 项链接与资源。浏览器验证原版搜索、Swup 进入论文页、PDF 中英文切换、12 项响应式页面检查、旧链接跳转，未出现脚本异常。

迁移仅修改配置与内容，新增 PDF／资源页，另修正两处上游组件类型兼容问题，未改造原版全局 CSS。
