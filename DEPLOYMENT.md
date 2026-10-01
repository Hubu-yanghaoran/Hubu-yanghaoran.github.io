# 首次部署新版个人主页

网站升级和笔记发布是两个步骤。先部署 website 中的新版源码，再使用 Local-Note-Publisher 发布笔记。不要把整个改进包、上传器目录或 ZIP 文件当作网站上传。

## 已准备好的部署副本

本次已从公开仓库克隆并合并新版，位置是：

```text
D:\AI workspace\ChatGPT\格基础学习\website-deployment-review
```

仓库： https://github.com/Hubu-yanghaoran/Hubu-yanghaoran.github.io

分支：main。核对时的原提交：1b31d4df0235851ef8ec95f68dd285969335f7bd。

这个目录包含 Git 历史与待提交的更改，可直接用 GitHub Desktop 打开，无需再次复制文件。当前没有新增提交，也没有推送到 GitHub。

1. 在 GitHub Desktop 登录你的 GitHub 账号。
2. 选择 File → Add local repository，选择上面的 website-deployment-review 文件夹。它已经是 Git 仓库，不要选择 Create a new repository。
3. 确认 Current branch 为 main，仓库名称为 Hubu-yanghaoran.github.io。Fetch origin 检查是否有新的远端提交；若显示落后，先处理远端变化，避免直接覆盖。
4. 查看 Changes。旧的根目录 index.html、notes.html、templates.html、lumina-guide.html 和三个生成的 JS 文件会显示删除：新版由 scripts/build.py 在 _site 中生成这些文件。源码中的 templates、assets、vendor 和 .github/workflows/pages.yml 必须包含在提交中。
5. 打开仓库 Settings → Pages，在 Build and deployment → Source 选择 **GitHub Actions**。配套工作流已经提供，无需再创建另一套工作流。
6. 在 Desktop 填写提交说明“升级学术主页布局与笔记阅读”，点击 Commit to main，再点击 Push origin。账号认证由 GitHub Desktop 处理。
7. 打开仓库 Actions，查看这次提交对应的 Build and publish academic homepage。validate 和 deploy 都成功后，打开 https://hubu-yanghaoran.github.io/ 验收。

源码仓库根目录没有 index.html 是正常的：发布的入口在构建产物 _site/index.html。不要切换为 Deploy from a branch 来直接发布源码根目录。

## 本次合并保留了什么

- 保留线上 content 和 notes 的内容、原始 Markdown 与附件，以及 notes-metadata.json。
- 线上目前只有一篇明确标记的测试笔记，未添加虚构成果或个人经历。
- 测试笔记的 note.json 增加 document_title，避免正文标题重复；更新“Markdown 不会排版”的过时说明。原 Markdown 文件没有改动。
- 新版资料配置采用 site-config.json；原有 site-config.js 是旧版生成文件。
- 本地生成的 _site、Python 缓存和上传器运行文件不提交。

本次部署副本已通过 13 项渲染测试、网站构建和 92 项本地链接/资源检查。真实 GitHub 认证、Pages 设置与远端 Actions 尚未验证。

## 以后上传笔记

1. 保留改进包中相邻的 website 与 Local-Note-Publisher 文件夹，双击 Local-Note-Publisher/start.cmd。
2. 选择文件或项目，填写标题、分类、摘要、标签与主文档。
3. 生成草稿并预览网页。
4. 仓库填写 https://github.com/Hubu-yanghaoran/Hubu-yanghaoran.github.io.git，填写你的提交姓名和邮箱，再点击发布。
5. 推送后点击“检查部署”，确认对应提交部署完成，最后打开网站检查。

上传器有自己的 checkout。不要把网站升级副本复制到上传器 checkout，也不要手动覆盖其恢复记录。

## 常见问题

| 现象 | 操作 |
| --- | --- |
| 只看到 validate 成功 | 继续检查 deploy；构建完成还不代表上线 |
| Pages 提示未配置 | 检查 Source 是否为 GitHub Actions |
| 工作流失败 | 查看失败步骤的日志，不反复上传相同文件 |
| 推送被拒绝 | 检查登录账号、仓库写入权限与远端更新，不使用强制推送 |
| 网站仍显示旧样式 | 对照此次提交的部署状态；成功后强制刷新浏览器 |
| 没有旧笔记 | 检查 content、notes、projects 是否被保留，再查看构建输出 |

GitHub 官方说明：[配置 Pages 发布来源](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)、[添加本地仓库到 GitHub Desktop](https://docs.github.com/en/desktop/adding-and-cloning-repositories/adding-a-repository-from-your-local-computer-to-github-desktop)。
