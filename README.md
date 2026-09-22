# Sunset Rush / 日不落狂飆

Babylon.js 3D 摩托車跑酷，支援 PC 鍵盤與手機滑動／觸控。

## 啟動

需要 Node.js 22 以上。

```sh
npm install
npm run dev
```

開啟 http://localhost:5173 。同 Wi-Fi 的手機使用電腦區網 IP 與 5173 連接埠。

```sh
npm test
npm start
```

不需要打包：瀏覽器透過 import map 直接載入 src/ 與本機安裝的 Babylon.js ESM 模組，CSS 使用 link 載入。沒有 Vite、轉譯或 dist 產物；修改後重新整理頁面即可。

Express 僅提供靜態檔案，可用 `PORT` 指定連接埠。排行榜不使用伺服器或資料庫。

## 操作與規則

- ← / → 或 A / D 換道，↑ / 空白鍵跳躍；手機左右／上滑及觸控按鈕。
- 四個車道均可進入：左側兩道對向、右側兩道順向；金幣、障礙物與跳板隨機分散在全部四道。
- 撞擊後停頓 0.7 秒並降速恢復；第三次碰撞結束。P / Escape 暫停。
- 跳板自動起跳，空中鎖定橫向位置與車道，落地後才能換道；速度隨距離增加；障礙間距與組合依種子變化。
- 道路有連續左右彎與高低起伏；四車道、車流、金幣、障礙與隧道沿同一路線排列，鏡頭跟隨彎向，騎士隨彎道傾斜。
- 城市 → 森林 → 隧道 → 海邊，每 360 公尺切換，日夜持續循環。
- 音效由開始遊戲的手勢啟動，可切換並保留偏好。

## 排行榜

成績存於此瀏覽器的 localStorage（sunset-rush-scores-v1），支援總榜與最近 24 小時。重新整理後保留；不同裝置、瀏覽器與網址不共用，清除網站資料會刪除成績。舊 SQLite 檔案保留但不再讀寫。

## 素材與修改

來源與授權見 `public/assets/ATTRIBUTION.md` 與 `public/assets/licenses/`。道路、建築、人物、車輛與收集物來自下載的 GLB 模型；全罩安全帽依參考輪廓製成獨立 GLB；沒有程式生成 SVG 或 Phaser Graphics 素材。路面及標線是從 Kenney 原模型中抽取既有三角面。速度線為非互動 HUD 動態效果；音效使用 Web Audio 合成。

## 驗證

`npm test` 包含不規則關卡、四車道邊界及物件分布、跳躍／跳板、三次撞擊停頓、加速、四場景靜態障礙通行路線、本機排行儲存、排序、日期篩選及重複紀錄測試。手機驗證使用瀏覽器 390×844 視窗與觸控按鈕，並非實體手機硬體效能測量。

## GitHub Pages

main 推送後由 GitHub Actions 發布。只複製原始 HTML、CSS、ESM、素材及 npm 安裝的 Babylon.js 模組，不進行打包或轉譯。所有網址採相對路徑，支援 /sunsetRush/ 子目錄。手動準備靜態目錄可執行 `node scripts/prepare-pages.js`。Pages 網址與 localhost 的 localStorage 分開保存。

## 精緻卡通渲染

使用 Poly by Google 的 CC BY 3.0 摩托車，將原模型車輪分離並保留原始配色，搭配 Quaternius 人形骨架騎士及貼合曲面面罩的全罩安全帽。骨架騎乘姿勢、手指握把、壓車和落地避震由呈現層控制，不修改碰撞與分數。車殼、輪胎、擋風鏡與燈具分材質，瀝青使用法線及粗糙度貼圖；夜間窗戶發光，車燈使用聚光燈，隧道循環使用三盞局部光源。

手機維持最高 2 倍像素解析度、1024 陰影與 2x MSAA（WebGL2）；電腦使用 2048 陰影、4x MSAA、輕量 SSAO 與 Bloom。WebGL1 回退至 FXAA。實體手機效能依裝置而異。

僅 localhost 可用 `?scene=tunnel&light=night` 檢查場景（city／forest／tunnel／coast），不增加遊戲畫面說明，也不影響正式站起始位置。

本機騎士檢驗：開啟 `http://localhost:5173/?rider=1`，可切換正面、側面、背面並進入實際遊玩。此介面僅在 localhost 啟用。
