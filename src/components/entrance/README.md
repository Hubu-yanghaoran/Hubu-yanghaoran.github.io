# 首次访问入场动画

`Layout.astro` 只需引入 `<Entrance name={siteConfig.title} />`。模块不修改 Fuwari 封面、头像或原版动画，不参与 Swup 内容替换。

在 `config.ts` 调整：

- `enabled`：模块开关；关闭后不输出动画元素。
- `duration`：毫秒，限制在 600–2400，默认 1200。
- `frequency`：`session` 每次浏览器会话首次访问播放；`once` 在当前浏览器首次访问播放。
- `storageKey`：记录播放状态；更换键可重新播放。
- `monogram`：中央字母标识；姓名来自站点配置。

样式集中在 `Entrance.astro`，逻辑在 `entrance.js`。动画不锁定滚动、不拦截点击、不移动焦点。禁用 JavaScript、拒绝存储或开启减少动态效果时直接显示网页。CSS 自行淡出，另有超时兜底；浏览器前进后退恢复页面时不会重播。
