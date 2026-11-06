
## XinghuisamaBlogs 功能参考（2026-11-06）

用户指定项目：[heiehiehi/XinghuisamaBlogs](https://github.com/heiehiehi/XinghuisamaBlogs)，查阅提交 8633e98。实际阅读 README、LICENSE、XHBlogs/components/SearchBar.tsx、GlobalToolbox.tsx、ClientTOC.tsx、TimelineClient.tsx、DailyBriefing.tsx 和配置。

- 搜索采用标题、描述和标签匹配，不是 PDF 全文检索。本站按用户要求独立实现更严格的默认“仅标题”，将原有全文能力收进高级搜索。
- 工具箱的注册表适合后续接入计算器、专注计时等独立工具。
- 时间线的主题筛选和视图切换可用于后续改进本站学习时间线。
- 每日选刊的收藏／已读状态可用于论文推荐阅读清单。
- 项目基于 Next.js / React，包含服务端 API 和本地管理端，不直接搬入当前 Astro 静态站点。Fuwari 已有目录跟随等功能，应优先沿用现有实现。

项目根许可为 CC BY-NC 4.0；本轮只分析功能思路，没有复制其代码或素材。未改动本站主题、封面或头像。
