**[[English version]][configuration]**
## 使用啟動參數  
可通過啟動參數啟用一項或多項功能。  

### 顯示幫助信息
#### 可執行檔
```
cd "專案路徑"
.\main.exe -h
```
#### Python 原始碼 (開發者適用)
```
cd "專案路徑"
python tools\main.py -h
```
> [!TIP]
> `專案路徑`為解壓縮後的資料夾路徑.  
> ![path]

### 幫助信息說明  
```
usage: main.py [-h] [-R] [-t] [-c] [-a] [-r] [-H] [-L] [-m] [-P] [-RC] [-SC] [-l] [-e] [-FB] [-GR] [-b] [-s] [-d] [-E]
               [-M] [-D] [-S] [-SO] [-SR] [-DM] [-GB] [-PVA] [-p PID | -N PROFILE_NAME] [-n FISH_COUNT]
               [-BT [DURATION]] [-T [DIRECTION]] [-BL [ACTION]]
               [opts ...]

啟動《俄羅斯釣魚4》自動腳本

位置參數:
  opts                  覆寫配置文件參數

選項:
  -h, --help            顯示幫助訊息
  -R, --rainbow         使用彩虹線計量器偵測收線
  -t, --tag             僅保留已標記的魚
  -c, --coffee          體力不足時飲用咖啡恢復體力
  -a, --alcohol         在保存魚之前飲酒
  -r, --refill          當飢餓或舒適度過低時自動補充茶與胡蘿蔔
  -H, --harvest         拋竿前自動收餌
  -L, --lure            定期隨機更換擬餌（僅限路亞模式）
  -m, --mouse           拋竿前隨機移動滑鼠
  -P, --pause           偶爾暫停腳本運行
  -RC, --random-cast    隨機添加額外拋竿動作
  -SC, --skip-cast      跳過首次拋竿直接開始收線
  -l, --lift            遛魚時持續提竿以節省時間
  -e, --electro         為Electro Raptor系列捲線器啟用電動模式
  -FB, --friction-brake 啟用自動摩擦調整
  -GR, --gear-ratio     收線超時後切換齒輪比
  -b, --bite            拋竿前截圖保存至 screenshots/（可用於分析咬鉤點）
  -s, --screenshot      捕獲魚隻後自動截圖保存
  -d, --data            在/logs目錄保存釣魚數據
  -E, --email           腳本停止後發送郵件通知
  -M, --miaotixing      腳本停止後發送喵提醒通知
  -D, --discord         腳本停止後發送Discord通知
  -S, --shutdown        腳本結束後關閉電腦
  -SO, --signout        退出遊戲而非關機
  -SR, --spod-rod       定期重拋餌料竿（底釣模式）
  -DM, --dry-mix        補充乾混合餌（底釣模式）
  -GB, --groundbait     補充底餌（底釣模式）
  -PVA, --pva           補充PVA餌（底釣模式）
  -p PID, --pid PID     指定配置檔ID
  -N PROFILE_NAME, --pname PROFILE_NAME
                        指定配置檔名稱
  -n FISH_COUNT, --fishes-in-keepnet FISH_COUNT
                        魚護當前魚量（預設為0）
  -BT [DURATION], --boat-ticket [DURATION]
                        自動續費船票，時長：1, 2, 3或5小時（預設5小時）
  -T [DIRECTION], --trolling [DIRECTION]
                        啟用拖釣模式，方向：'forward','left','right'（預設按'j'前進）
  -BL [ACTION], --broken-lure [ACTION]
                        斷餌自動處理，操作：'replace'或'alarm'（預設更換）
``` 

> [!IMPORTANT]
> 若需使用 `-r` 或 `-c` 參數，請將茶和胡蘿蔔/咖啡加入 **[收藏物品][favorite_food]**。  
> 需自動更換物品的功能，請將相關物品加入 **[收藏物品][favorite_lure]**。

### 使用示例  
**設置魚護當前魚量為32條（需捕獲68條）：**  
```  
python tools\main.py -n 32  
```  

**使用3號配置檔，遛魚時飲用咖啡，停止後發送郵件：**  
```  
python tools\main.py -p 3 --c --email  
```  

**自動補充體力/飢餓/舒適度，拋竿前收餌：**  
```  
python tools\main.py -rcH  
```  

**定期重拋餌料竿並補充乾混合餌：**  
```  
python tools\main.py -o -dm  
```  

## 配置文件  
### 修改設置  
編輯`config.yaml`後重新運行腳本即可生效。  
各項參數詳解參見[配置參數說明](#配置參數說明)。  

### 添加新配置檔  
1. 複製現有配置檔結構  
2. 修改參數後添加至`PROFILE`段落  

示例添加名為`YOUR_NEW_PROFILE`的路亞配置：  
```yaml  
PROFILE:  
  SPIN:   
    MODE: "spin"  
    CAST_POWER_LEVEL: 5.0  
    CAST_DELAY: 6.0  
    ...  
  
  YOUR_NEW_PROFILE:  
    MODE: "spin"  
    CAST_POWER_LEVEL: 5.0  
    CAST_DELAY: 4.0  # 縮短拋竿延遲  
    PRE_ACCELERATION: True  # 啟用預加速  
    ...  
```  

> [!IMPORTANT]  
> - 配置檔名稱需唯一  
> - 嚴格保持縮進格式  
> - `MODE`需為`spin`/`bottom`/`pirk`/`elevator`/`telescopic`/`bolognese`  

### 臨時覆寫配置  
無需修改文件，直接通過命令覆寫參數：  
```  
python tools\main.py SCRIPT.LANGUAGE "ru"  # 臨時設置腳本語言為俄語  
```  

### 雙竿拖釣模式  
組合底釣配置與`-T`參數實現：  
```  
python tools\main.py -T KEY.BOTTOM_RODS "1, 2"  # 指定使用1、2號快捷鍵位  
```  


## 配置參數說明  
```python  
"""YACS默認配置節點"""  

from yacs.config import CfgNode as CN  

_C = CN()  
_C.VERSION = "0.0.0"  

# --------------------------------- 通用設置 -------------------------------- #  
_C.SCRIPT = CN()  
_C.SCRIPT.LANGUAGE = "en" # 腳本語言: en/ru/zh-TW/zh-CN  
_C.SCRIPT.LAUNCH_OPTIONS = ""  # 默認啟動參數，如"-r -c -H"  
_C.SCRIPT.SMTP_VERIFICATION = True  # SMTP驗證  
_C.SCRIPT.IMAGE_VERIFICATION = True  # 圖像驗證  
_C.SCRIPT.SNAG_DETECTION = True  # 掛底檢測  
_C.SCRIPT.SPOOLING_DETECTION = True  # 線軸檢測  
_C.SCRIPT.RANDOM_ROD_SELECTION = True  # 底釣隨機選竿  
_C.SCRIPT.SPOOL_CONFIDENCE = 0.98  # 線軸檢測敏感度（值越低越敏感）  
_C.SCRIPT.SPOD_ROD_RECAST_DELAY = 1800  # 餌料竿重拋間隔（秒）  
_C.SCRIPT.LURE_CHANGE_DELAY = 1800  # 擬餌更換間隔（秒）  
_C.SCRIPT.ALARM_SOUND = "./static/sound/guitar.wav"  # 提示音文件路徑
_C.SCRIPT.RANDOM_CAST_PROBABILITY = 0.25 # 隨機拋竿失誤的機率
_C.SCRIPT.SCREENSHOT_TAGS = ( # 魚獲截圖的標記種類，列表為空的話所有的魚都會截圖
    "green",
    "yellow",
    "blue",
    "purple",
    "pink"
)

# --------------------------------- 快捷鍵設置 ------------------------------ #  
_C.KEY = CN()  
_C.KEY.TEA = -1  # 茶快捷鍵（-1使用快捷菜單）  
_C.KEY.CARROT = -1  # 胡蘿蔔快捷鍵  
_C.KEY.BOTTOM_RODS = (1, 2, 3)  # 底釣竿快捷鍵位  
_C.KEY.COFFEE = 4  # 咖啡快捷鍵  
_C.KEY.DIGGING_TOOL = 5  # 挖餌工具快捷鍵  
_C.KEY.ALCOHOL = 6  # 酒精飲品快捷鍵  
_C.KEY.MAIN_ROD = 1  # 主釣竿快捷鍵  
_C.KEY.SPOD_ROD = 7  # 餌料竿快捷鍵  
_C.KEY.QUIT = "CTRL-C"  # 退出快捷鍵  

# --------------------------------- 角色狀態 -------------------------------- #  
_C.STAT = CN()  
_C.STAT.ENERGY_THRESHOLD = 0.74  # 喝咖啡/收餌體力閾值  
_C.STAT.HUNGER_THRESHOLD = 0.5  # 食用胡蘿蔔飢餓閾值  
_C.STAT.COMFORT_THRESHOLD = 0.51  # 飲茶舒適度閾值  
_C.STAT.TEA_DELAY = 300  # 飲茶間隔（秒）  
_C.STAT.COFFEE_LIMIT = 10  # 單次遛魚最大咖啡飲用量  
_C.STAT.COFFEE_PER_DRINK = 1  # 單次飲用咖啡量  
_C.STAT.ALCOHOL_DELAY = 900  # 飲酒間隔（秒）  
_C.STAT.ALCOHOL_PER_DRINK = 1  # 單次飲酒量  

# ----------------------------- 摩擦剎車設置（需-f參數）----------------------- #  
_C.FRICTION_BRAKE = CN()  
_C.FRICTION_BRAKE.INITIAL = 29  # 初始剎車值  
_C.FRICTION_BRAKE.MAX = 30  # 最大剎車值  
_C.FRICTION_BRAKE.START_DELAY = 2.0  # 中魚後開始調整延遲（秒）  
_C.FRICTION_BRAKE.INCREASE_DELAY = 1.0  # 剎車增強間隔  
_C.FRICTION_BRAKE.SENSITIVITY = "medium"  # 檢測敏感度（low/medium/high）  

# --------------------------------- 魚護設置 -------------------------------- #  
_C.KEEPNET = CN()  
_C.KEEPNET.CAPACITY = 100  # 魚護容量  
_C.KEEPNET.FISH_DELAY = 0.0  # 存魚前延遲（用於截圖）
_C.KEEPNET.GIFT_DELAY = 4.0  # 接受禮物前延遲（用於截圖）
_C.KEEPNET.FULL_ACTION = "quit"  # 滿護操作：quit（退出）/alarm（警報）
# -m模式保留魚種
# 選項: mackerel, saithe, herring, squid, scallop, mussel, perch, shorthorn_sculpin
_C.KEEPNET.WHITELIST = (  # -t模式保留魚種  
    "mackerel", "saithe", "herring",  
    "squid", "scallop", "mussel"  
)
# 魚種黑名單
# 選項: mackerel, saithe, herring, squid, scallop, mussel, perch, shorthorn_sculpin
_C.KEEPNET.BLACKLIST = (
)
# -t模式保留魚的標記種類
_C.KEEPNET.TAGS = (
    "green",
    "yellow",
    "blue"
    "purple",
    "pink"
)

# ----------------------------- 通知設置 -------------------------------- #  
_C.NOTIFICATION = CN()  
_C.NOTIFICATION.EMAIL = "email@example.com"  # 郵箱地址  
_C.NOTIFICATION.PASSWORD = "password"  # 郵箱密碼  
_C.NOTIFICATION.SMTP_SERVER = "smtp.gmail.com"  # SMTP服務器  
_C.NOTIFICATION.MIAO_CODE = "example"  # 喵提醒識別碼
_C.NOTIFICATION.DISCORD_WEBHOOK_URL = "" # Discord Webhook 鍊結

# ----------------------------- 暫停設置（需-X參數）------------------------ #  
_C.PAUSE = CN()  
_C.PAUSE.DELAY = 1800  # 暫停間隔（秒）  
_C.PAUSE.DURATION = 600  # 暫停時長（秒）  

# ----------------------------- 配置檔詳解 -------------------------------- #  
_C.PROFILE = CN()  

## 路亞配置 ##  
_C.PROFILE.SPIN = CN()  
_C.PROFILE.SPIN.MODE = "spin"  
# 用於覆蓋 SCRIPT.LAUNCH_OPTIONS 的啟動參數
# 若未設置，將使用 SCRIPT.LAUNCH_OPTIONS 作為預設值
_C.PROFILE.SPIN.LAUNCH_OPTIONS = ""
_C.PROFILE.SPIN.CAST_POWER_LEVEL = 5.0  # 拋投力度等級（1~5級，5為全力拋投）  
_C.PROFILE.SPIN.CAST_DELAY = 6.0  # 拋竿後等待時間（秒）  
_C.PROFILE.SPIN.TIGHTEN_DURATION = 0.0  # 收緊釣線時長（秒）  
_C.PROFILE.SPIN.RETRIEVAL_DURATION = 0.0  # 收線/提竿持續時間（秒）  
_C.PROFILE.SPIN.RETRIEVAL_DELAY = 0.0  # 收線後延遲（秒）  
_C.PROFILE.SPIN.RETRIEVAL_TIMEOUT = 256.0 # 打狀態超時 （秒）
_C.PROFILE.SPIN.PRE_ACCELERATION = False  # 拋竿前按住Shift（特殊技法）  
_C.PROFILE.SPIN.POST_ACCELERATION = "off"  # 遛魚時加速模式（on/off/auto）  
_C.PROFILE.SPIN.TYPE = "normal"  # 操作類型：normal（常規）/pause（停頓）/lift（提拉）  

## 底釣配置 ##  
_C.PROFILE.BOTTOM = CN()
# 用於覆蓋 SCRIPT.LAUNCH_OPTIONS 的啟動參數
# 若未設置，將使用 SCRIPT.LAUNCH_OPTIONS 作為預設值
_C.PROFILE.BOTTOM.LAUNCH_OPTIONS = ""
_C.PROFILE.BOTTOM.MODE = "bottom"  
_C.PROFILE.BOTTOM.CAST_POWER_LEVEL = 5.0  # 拋投力度  
_C.PROFILE.BOTTOM.CAST_DELAY = 4.0  # 拋竿後等待時間（秒）  
_C.PROFILE.BOTTOM.POST_ACCELERATION = "off"  # 遛魚加速模式  
_C.PROFILE.BOTTOM.CHECK_DELAY = 32.0  # 檢查咬口間隔（秒）  
_C.PROFILE.BOTTOM.CHECK_MISS_LIMIT = 16  # 最大空竿次數後重拋  
_C.PROFILE.BOTTOM.PUT_DOWN_DELAY = 0.0  # 放下竿子前再次檢查延遲

## 海釣/維基配置（Pirk技法）##  
_C.PROFILE.PIRK = CN()  
_C.PROFILE.PIRK.MODE = "pirk"
# 用於覆蓋 SCRIPT.LAUNCH_OPTIONS 的啟動參數
# 若未設置，將使用 SCRIPT.LAUNCH_OPTIONS 作為預設值
_C.PROFILE.PIRK.LAUNCH_OPTIONS = ""
_C.PROFILE.PIRK.CAST_POWER_LEVEL = 1.0  # 拋投力度（淺拋）  
_C.PROFILE.PIRK.CAST_DELAY = 4.0  # 拋竿後等待時間（秒）  
_C.PROFILE.PIRK.SINK_TIMEOUT = 60.0  # 餌沉底超時（秒）  
_C.PROFILE.PIRK.TIGHTEN_DURATION = 1.0  # 收線緊繃時長（秒）
_C.PROFILE.PIRK.DEPTH_ADJUST_DELAY = 4.0  # 調整深度延遲（秒）  
_C.PROFILE.PIRK.DEPTH_ADJUST_DURATION = 1.0 # 調整深度後的收線時長（秒）
_C.PROFILE.PIRK.CTRL = False  # 抽竿時按住Ctrl
_C.PROFILE.PIRK.SHIFT = False  # 抽竿時按住Shift
_C.PROFILE.PIRK.PIRK_DURATION = 0.5  # 抽竿時長（秒）  
_C.PROFILE.PIRK.PIRK_DELAY = 2.0  # 抽竿後延遲（秒）  
_C.PROFILE.PIRK.PIRK_TIMEOUT = 32.0  # 抽竿超時（秒）  
_C.PROFILE.PIRK.PIRK_RETRIEVAL = False  # 抽竿時收線  
_C.PROFILE.PIRK.HOOK_DELAY = 0.5  # 中魚後檢查延遲（秒）  
_C.PROFILE.PIRK.POST_ACCELERATION = "auto"  # 遛魚加速模式 

## 升降釣法配置（深海升降釣組）##  
_C.PROFILE.ELEVATOR = CN()
_C.PROFILE.ELEVATOR.MODE = "elevator"
# 用於覆蓋 SCRIPT.LAUNCH_OPTIONS 的啟動參數
# 若未設置，將使用 SCRIPT.LAUNCH_OPTIONS 作為預設值
_C.PROFILE.ELEVATOR.LAUNCH_OPTIONS = ""
_C.PROFILE.ELEVATOR.CAST_POWER_LEVEL = 1.0  # 拋投力度等級（1~5級，1為輕拋）  
_C.PROFILE.ELEVATOR.CAST_DELAY = 4.0  # 拋竿後等待時間（秒）  
_C.PROFILE.ELEVATOR.SINK_TIMEOUT = 60.0  # 餌沉底超時（秒）  
_C.PROFILE.ELEVATOR.TIGHTEN_DURATION = 1.0  # 收緊釣線時長（秒）  
_C.PROFILE.ELEVATOR.ELEVATE_DURATION = 4.0  # 提升釣線持續時間（秒）  
_C.PROFILE.ELEVATOR.ELEVATE_DELAY = 4.0  # 提升後延遲（秒）  
_C.PROFILE.ELEVATOR.ELEVATE_TIMEOUT = 40.0  # 單次升降超時（秒）  
_C.PROFILE.ELEVATOR.DROP = False  # 超時後自動下沉釣組（逐層下降）  
_C.PROFILE.ELEVATOR.HOOK_DELAY = 0.5  # 中魚後檢查延遲（秒）  
_C.PROFILE.ELEVATOR.POST_ACCELERATION = "auto"  # 遛魚加速模式（on/off/auto）

## 浮標釣配置 ##  
_C.PROFILE.TELESCOPIC = CN()  
_C.PROFILE.TELESCOPIC.MODE = "telescopic"
# 用於覆蓋 SCRIPT.LAUNCH_OPTIONS 的啟動參數
# 若未設置，將使用 SCRIPT.LAUNCH_OPTIONS 作為預設值
_C.PROFILE.TELESCOPIC.LAUNCH_OPTIONS = ""
_C.PROFILE.TELESCOPIC.CAST_POWER_LEVEL = 5.0  # 拋投力度  
_C.PROFILE.TELESCOPIC.CAST_DELAY = 4.0  # 拋竿後等待時間（秒）  
_C.PROFILE.TELESCOPIC.FLOAT_SENSITIVITY = 0.68  # 浮標檢測敏感度（0~1）  
_C.PROFILE.TELESCOPIC.CHECK_DELAY = 1.0  # 檢查咬口間隔（秒）  
_C.PROFILE.TELESCOPIC.PULL_DELAY = 0.5  # 中魚後提竿延遲（秒）  
_C.PROFILE.TELESCOPIC.DRIFT_TIMEOUT = 16.0  # 漂流超時重拋（秒）  
_C.PROFILE.TELESCOPIC.CAMERA_SHAPE = "square"  # 浮標視窗形狀（square/wide/tall）  

## 博洛尼亞釣法配置 ##  
_C.PROFILE.BOLOGNESE = CN()  
_C.PROFILE.BOLOGNESE.MODE = "bolognese"
# 用於覆蓋 SCRIPT.LAUNCH_OPTIONS 的啟動參數
# 若未設置，將使用 SCRIPT.LAUNCH_OPTIONS 作為預設值
_C.PROFILE.BOLOGNESE.LAUNCH_OPTIONS = ""
_C.PROFILE.BOLOGNESE.CAST_POWER_LEVEL = 5.0  # 拋投力度  
_C.PROFILE.BOLOGNESE.CAST_DELAY = 4.0  # 拋竿後等待時間（秒）  
_C.PROFILE.BOLOGNESE.FLOAT_SENSITIVITY = 0.68  # 浮標檢測敏感度  
_C.PROFILE.BOLOGNESE.DRIFT_TIMEOUT = 32.0  # 漂流超時重拋（秒）
_C.PROFILE.BOLOGNESE.POST_ACCELERATION = "off"  # 遛魚加速模式（on/off/auto）

def get_cfg_defaults():  
    """獲取默認配置節點"""  
    return _C.clone()  
```  


## 喵提醒的MIAO_CODE配置方式
1. 關注微信公衆號 **[喵提醒][meow]**。
   
2. 新建提醒服務  
![meow_1] ![meow_2]

3. 效果展示  
![meow_3]

[configuration]: /docs/en/CONFIGURATION.md
[favorite_food]: /static/readme/favorite_food.png
[favorite_lure]: /static/readme/favorite_lure.png
[meow]: https://miaotixing.com/how
[meow_1]: /static/readme/mtx1.png
[meow_2]: /static/readme/mtx2.png
[meow_3]: /static/readme/mtx3.png