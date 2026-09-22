# 素材狀態：已補齊目前版本

已依使用者授權取得正式 GLB 素材，現行來源、修改與授權見 `../public/assets/ATTRIBUTION.md`。目前版本包含城市、森林、隧道與海邊。下列為初始規格歷史，實際操作與規則以 README.md 為準。

# Speed Run：3D 摩托車跑酷素材待補清單

目前專案為空，尚無遊戲素材。依使用者規則，素材補齊或取得明確指示前不撰寫遊戲程式，不使用程式圖形、SVG 或色塊替代正式素材。

## 預定遊戲規格

- 引擎：Babylon.js；瀏覽器 3D，PC 與手機均可遊玩。
- 玩法：第三人稱追尾視角、自動前進、三車道穿梭、跳躍、收集、碰撞結算、逐漸加速；障礙排列須保留可通過路徑。
- 主角：戴安全帽的卡通騎士與摩托車；轉向傾斜、起跳、空中姿勢與落地緩衝。
- PC：A/D 或左右方向鍵換道，空白鍵／上方向鍵跳躍。
- 手機：左右滑動換道、上滑跳躍，另提供大型觸控按鈕。
- 世界：道路無限延伸，白天 → 黃昏 → 夜晚 → 清晨平滑循環；夜間保持障礙辨識度。
- 排行榜：規劃共用後端持久化排行榜，按分數排序，距離作為次排序；伺服器驗證遊戲紀錄，不直接信任瀏覽器提交的總分。公開上線需要後端部署。
- 視覺：圓潤、明亮、低多邊形卡通城市；碰撞無血腥。

## 必要素材

真正 3D 主角與道路需要 GLB/glTF 模型，PNG 只適合貼圖與 UI。採用現成授權 3D 模型及 PNG/WebP 貼圖的方向，待使用者明確指示後執行。

| 名稱 | 格式／建議規格 | 風格與用途 |
| --- | --- | --- |
| 摩托車與騎士 | GLB，主角合計約 10k–25k 三角面，1024² 貼圖 | 圓潤小型街車、安全帽；輪子可旋轉、騎士可調整姿勢 |
| 動作 | GLB 動畫或可動畫骨架／節點 | 騎乘、左傾、右傾、跳躍、落地 |
| 路面模組 | GLB，統一三車道寬度，512–1024² 貼圖 | 可無縫銜接道路、路緣、人行道 |
| 車流 | GLB，3–5 種，512–1024² 貼圖 | 汽車、貨車、公車；清楚辨識碰撞範圍 |
| 障礙與跳台 | GLB，4–6 種，512² 貼圖 | 路障、交通錐、可跳越矮障礙、跳台 |
| 城市佈景 | GLB，建築 6 種以上，樹木與路燈 | 沿路重複組合，夜晚可亮窗與路燈 |
| 收集物 | GLB 或正式 PNG 圖集，256–512² | 明亮易辨識的代幣 |
| 天空 | 無縫全景 PNG/JPG，2048×1024，日／昏／夜／晨 | 同一地平線可平滑過渡，無文字 |
| UI 圖像 | PNG/WebP，64–256² 圖示、512×128 按鈕 | 跳躍、方向、暫停、音量、獎盃；清楚易讀 |
| 音效與音樂 | OGG/MP3/WAV | 引擎、收集、跳躍、落地、碰撞、輕快循環音樂 |

## 可使用的免費素材來源

- Kenney Car Kit：https://kenney.nl/assets/car-kit （官方標示 CC0；可補交通工具，尚未下載或確認是否含適用摩托車）
- Kenney 素材庫：https://kenney.nl/assets/ （道路、建築、UI；逐包確認內容）
- Quaternius：https://quaternius.com/ （搜尋卡通 3D 模型；逐包確認授權與模型內容）
- OpenGameArt：https://opengameart.org/ （音效與貼圖；逐項確認授權與署名要求）

下載後需記錄來源 URL、作者、授權、修改內容；主角模型須先檢視才算可用。

## 可直接使用的圖像生成提示詞

主角概念圖（僅用於設計參考，不能代替可遊玩的 3D 模型）：

“Original family-friendly cartoon motorcycle rider wearing a full helmet, rounded compact turquoise and coral street motorcycle, appealing low-poly game art direction, readable silhouette, front side and rear orthographic turnaround, consistent proportions, neutral lighting, plain background, no text, no logos, 2048x2048.”

天空背景（四張保持相同地平線）：

“Seamless equirectangular cartoon sky panorama, soft rounded clouds, cheerful family-friendly mobile racing game, unobstructed sky, no buildings, no text, 2048x1024. Create consistent daylight, sunset, moonlit night and dawn variants with matching horizon.”

UI 圖示圖集：

“Cartoon mobile motorcycle runner UI icon sheet, jump arrow, left arrow, right arrow, pause, sound, trophy, rounded polished shapes, turquoise coral and cream palette, high contrast, consistent padding, transparent background, no text, 1024x1024.”

## 待使用者選擇

1. 授權先尋找、下載免費授權 3D 模型與圖像素材，再開始實作（建議）。
2. 使用者自行提供摩托車／騎士 GLB 與其他素材。
3. 先製作卡通視覺概念圖，再確定 3D 素材取得方式。
