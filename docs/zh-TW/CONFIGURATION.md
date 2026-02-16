# 設定 RF4S

---

## 介面語言

RF4S 支援**英文**（`en`）和**俄文**（`ru`）介面。`config.yaml` 中的 `LANGUAGE` 參數決定：
- 用於遊戲元素辨識的圖片集（`static/en/` 或 `static/ru/`）

```yaml
# 英文
LANGUAGE: "en"

# 俄文
LANGUAGE: "ru"
```

> [!IMPORTANT]
> `LANGUAGE` 的值必須與 Russian Fishing 4 遊戲中設定的語言一致。

透過命令列一次性覆寫（不修改設定檔）：
```
python main.py LANGUAGE "ru"
```

---

## 啟動選項

啟動選項可在腳本啟動時啟用功能。

### 啟動方式

**執行檔：**
```
.\main.exe [指令] [選項]
```

**Python：**
```
python main.py [指令] [選項]
```

**uv：**
```
uv run main.py [指令] [選項]
```

> [!NOTE]
> 若未指定選項（或透過雙擊啟動），腳本將進入互動模式：顯示功能列表，提示選擇編號並輸入選項。
>
> ![啟動選項][launch_options]

### 互動模式

無參數啟動時：
1. 顯示功能列表（0-5）
2. 輸入功能編號，`h` 查看說明，`q` 退出
3. 輸入啟動選項或按 Enter 跳過

---

## 指令

### 1. `bot` — 釣魚機器人

自動化釣魚流程。

```
python main.py bot [選項]
```

#### 主要選項

| 選項 | 說明 |
|---|---|
| `-V`, `--version` | 顯示版本並退出 |
| `-p PID`, `--pid PID` | 指定設定檔 ID（0-N） |
| `-N 名稱`, `--pname 名稱` | 指定設定檔名稱 |
| `-n 數量`, `--fishes-in-keepnet 數量` | 護網中已有的魚數（預設：0） |

#### 釣魚模式

| 選項 | 說明 | 值 |
|---|---|---|
| `-T [方向]`, `--trolling [方向]` | 拖釣模式 | `forward`、`left`、`right`（預設：`forward`） |
| `-R [公尺]`, `--rainbow [公尺]` | 彩虹線模式 | `0`、`5`（預設：`5`） |
| `-BT [天數]`, `--boat-ticket [天數]` | 自動續購船票 | `1`、`2`、`3`、`5`（預設：`5`） |

#### 旗標：魚類管理

| 旗標 | 說明 |
|---|---|
| `-t`, `--tag` | 僅保留已標記的魚 |
| `-c`, `--coffee` | 收線時體力不足時喝咖啡 |
| `-a`, `--alcohol` | 保存魚之前喝酒 |
| `-l`, `--lift` | 收線時持續提竿 |

#### 旗標：釣具與餌料

| 旗標 | 說明 |
|---|---|
| `-L`, `--lure` | 更換為隨機收藏餌料（模式：路亞） |
| `-BL`, `--broken-lure` | 將損壞的餌料替換為收藏餌料 |
| `-e`, `--electro` | Electro Raptor 系列捲線器的電動模式 |
| `-FB`, `--friction-brake` | 自動調整煞車 |
| `-GR`, `--gear-ratio` | 捲線逾時後切換齒輪比 |

#### 旗標：窩料（底釣）

| 旗標 | 說明 |
|---|---|
| `-DM`, `--dry-mix` | 補充乾混合料 |
| `-GB`, `--groundbait` | 補充窩料 |
| `-PVA`, `--pva` | 補充 PVA 袋 |
| `-SR`, `--spod-rod` | 重新拋投窩料竿 |

#### 旗標：機器人行為

| 旗標 | 說明 |
|---|---|
| `-r`, `--refill` | 飢餓或舒適度低時食用茶和胡蘿蔔 |
| `-H`, `--harvest` | 拋竿前採集餌料 |
| `-m`, `--mouse` | 拋竿前隨機移動滑鼠 |
| `-P`, `--pause` | 拋竿前偶爾暫停腳本 |
| `-RC`, `--random-cast` | 進行隨機額外拋竿 |
| `-SC`, `--skip-cast` | 跳過第一次拋竿 |
| `-NA`, `--no-animation` | 停用獎盃和禮物動畫等待 |

#### 旗標：記錄與通知

| 旗標 | 說明 |
|---|---|
| `-b`, `--bite` | 咬餌時截圖（`screenshots/`） |
| `-s`, `--screenshot` | 釣到魚後截圖（`screenshots/`） |
| `-d`, `--data` | 將釣魚資料儲存至 `/logs` |
| `-E`, `--email` | 停止時發送電子郵件通知 |
| `-M`, `--miaotixing` | 停止時發送喵提醒通知 |
| `-D`, `--discord` | 停止時發送 Discord 通知 |
| `-TG`, `--telegram` | 停止時發送 Telegram 通知 |

#### 旗標：停止後操作

| 旗標 | 說明 |
|---|---|
| `-S`, `--shutdown` | 關閉電腦 |
| `-SO`, `--signout` | 登出帳號而非關閉遊戲 |

#### 範例

```bash
# 使用設定檔 0 的機器人，啟用自動煞車
python main.py bot -p 0 -FB

# 使用命名設定檔的機器人，儲存截圖
python main.py bot -N "MyProfile" -s -b

# 向前拖釣搭配彩虹線
python main.py bot -T forward -R 5

# 搭配窩料的底釣
python main.py bot -DM -GB -PVA

# 恢復狀態 + 採集餌料 + 咖啡
python main.py bot -rcH
```

> [!IMPORTANT]
> 使用 `-r` 和 `-c` 時，請將茶、胡蘿蔔和咖啡加入**[收藏][favorite_food]**。
> 使用自動更換釣具功能時，請將物品加入**[收藏][favorite_lure]**。

---

### 2. `craft` — 製作物品

自動製作餌料、窩料、擬餌等。

```
python main.py craft [選項]
```

| 選項 | 說明 |
|---|---|
| `-V`, `--version` | 顯示版本 |
| `-d`, `--discard` | 丟棄所有製作的物品（用於窩料） |
| `-i`, `--ignore` | 忽略未選擇的材料欄位 |
| `-n 數量`, `--craft-limit 數量` | 物品數量（預設：-1，無限） |

```bash
# 製作 10 個物品
python main.py craft -n 10

# 製作窩料並丟棄
python main.py craft -d
```

---

### 3. `move` — 向前移動

切換角色向前移動（按住 `W` 鍵）。

```
python main.py move [選項]
```

| 選項 | 說明 |
|---|---|
| `-V`, `--version` | 顯示版本 |
| `-s`, `--shift` | 移動時按住 Shift（奔跑） |

```bash
# 一般移動
python main.py move

# 按住 Shift 奔跑
python main.py move -s
```

---

### 4. `harvest` — 採集餌料

在待機模式下自動採集餌料。

```
python main.py harvest [選項]
```

| 選項 | 說明 |
|---|---|
| `-V`, `--version` | 顯示版本 |
| `-r`, `--refill` | 用茶和胡蘿蔔補充飢餓與舒適度 |

```bash
# 簡單採集餌料
python main.py harvest

# 採集並恢復狀態
python main.py harvest -r
```

---

### 5. `frictionbrake`（或 `fb`）— 自動煞車

自動調整捲線器的煞車。

```
python main.py frictionbrake
python main.py fb
```

| 選項 | 說明 |
|---|---|
| `-V`, `--version` | 顯示版本 |

---

### 6. `calculate`（或 `cal`）— 釣具計算器

計算釣具屬性和考慮磨損的建議煞車值。

```
python main.py calculate
python main.py cal
```

| 選項 | 說明 |
|---|---|
| `-V`, `--version` | 顯示版本 |

---

## 運行時快捷鍵

在 `config.yaml` 中設定（`KEY` 區段）：

| 預設按鍵 | 操作 | 設定參數 |
|---|---|---|
| `[` | 暫停 / 繼續（機器人） | `KEY.PAUSE` |
| `Ctrl+C` | 終止腳本 | `KEY.QUIT` |
| `[` | 重置煞車 | `KEY.FRICTION_BRAKE_RESET` |
| `]` | 退出煞車模式 | `KEY.FRICTION_BRAKE_QUIT` |
| `w` | 暫停移動 | `KEY.MOVE_PAUSE` |
| `s` | 退出移動模式 | `KEY.MOVE_QUIT` |

---

## 設定檔

所有設定儲存在專案根目錄的 `config.yaml` 中。變更在重新啟動後生效。

所有參數參考：[`defaults.py`][default.py]

### 主要參數

| 參數 | 說明 | 值 |
|---|---|---|
| `LANGUAGE` | 介面與辨識語言 | `"en"`、`"ru"` |
| `BOT.CLICK_LOCK` | Windows 滑鼠鎖定點擊 | `true`、`false` |
| `BOT.KEEPNET.CAPACITY` | 護網容量 | 數字 |
| `BOT.SPOOL_CONFIDENCE` | 線軸偵測靈敏度 | `0.0`-`1.0` |
| `BOT.JITTER_SCALE` | 隨機延遲比例 | 數字 |

---

## 設定檔（Profiles）

設定檔可讓您儲存不同釣魚風格的設定。

### 新增設定檔

從設定中複製現有設定檔，編輯後加入 `PROFILE` 區段：

```yaml
PROFILE:
  BOTTOM:
    DESCRIPTION: "預設底釣模式。"
    LAUNCH_OPTIONS: ""
    MODE: "bottom"
    CAST_POWER_LEVEL: 5.0
    CAST_DELAY: 4.0
    POST_ACCELERATION: false
    CHECK_DELAY: 16.0
    CHECK_MISS_LIMIT: 16
    PUT_DOWN_DELAY: 2.0
    RANDOM_ROD_SELECTION: true
            .
            .
            .
  MY_BOTTOM_FISHING:
    DESCRIPTION: "我的底釣設定。"
    LAUNCH_OPTIONS: "-rctdDR"
    MODE: "bottom"
    CAST_POWER_LEVEL: 5.0
    CAST_DELAY: 4.0
    POST_ACCELERATION: false
    CHECK_DELAY: 16.0
    CHECK_MISS_LIMIT: 64
    PUT_DOWN_DELAY: 4.0
    RANDOM_ROD_SELECTION: false
```

> [!IMPORTANT]
> - 設定檔名稱必須**唯一**。
> - 請確保正確的**縮排**（YAML 對縮排敏感）。
> - `MODE` 的有效值：`spin`、`bottom`、`pirk`、`elevator`、`telescopic`、`bolognese`。

---

## 覆寫設定

可以透過命令列參數暫時更改 `config.yaml` 中的任何參數，而無需編輯檔案：

```
.\main.exe LANGUAGE "ru"
```
```
.\main.exe bot BOT.KEEPNET.CAPACITY 200
```

這對於使用非標準設定的一次性啟動非常方便。

---

## 雙竿拖釣

船上拖釣本質上是按住移動鍵的底釣。使用底釣設定檔搭配 `-T` 旗標：

```
.\main.exe bot -T KEY.BOTTOM_RODS "(1, 2)"
```

船上沒有第三支竿架，因此將竿的按鍵覆寫為 `1` 和 `2`。

---

## 資料夾結構

啟動後自動建立以下資料夾：

| 資料夾 | 內容 |
|---|---|
| `screenshots/` | 咬餌和釣到魚的截圖 |
| `logs/` | 執行記錄、釣魚資料、圖表 |

[launch_options]: /static/readme/launch_options.png
[config.yaml]: /rf4s/config/config.yaml
[default.py]: /rf4s/config/defaults.py
[favorite_food]: /static/readme/favorite_food.png
[favorite_lure]: /static/readme/favorite_lure.png
