# 2026/10 墨爾本之旅隨身網頁

10/09–10/13 墨爾本家庭之旅的手機隨身頁，分三個區塊：

- **行程**：依當地時間顯示下一站、按天分頁的行程與天氣、選區看附近景點與導航
- **清單**：出國整理清單，可打勾，狀態存在手機瀏覽器
- **指南**：落地出關→SkyBus、SkyBus 搭乘、叫車與兒童座椅規定、景點地圖連結、實用資訊

網頁：https://jameskan-tw.github.io/travel-melbourne/

## 結構

- `src/template.html`：頁面模板（含行程資料與腳本）
- `../出國清單.md`、`../SkyBus指南.md`、`../叫車指南.md`、`../景點清單.md`：清單與指南內容
- `build.py`：把 md 轉成 HTML 注入模板，產出 `index.html`（GitHub Pages）與 `artifact.html`（Claude Artifact）

```bash
python3 build.py
```

景點座標、開放時間與票價為 2026/10/05–07 查證，出發前請再核對官方資訊。
