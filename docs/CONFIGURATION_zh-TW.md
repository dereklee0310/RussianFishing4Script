作者很懶，直接把丟給DeepSeek R1生成🤗

**[[英文版]][Configuration guide]**

# 配置指南  

## 使用啟動參數  
可通過啟動參數啟用一項或多項功能。  

### 顯示幫助信息  
```  
python tools\main.py -h  
```  

### 幫助信息說明  
```  
usage: main.py [-h] [-c] [-A] [-r] [-H] [-g] [-f] [-l] [-C] [-o] [-L] [-x] [-X] [-b] [-S] [-e] [-P] [-M] [-s] [-so]  
               [-gb] [-dm] [-pva] [-E] [-a | -m] [-d | -R] [-p PID | -N PROFILE_NAME] [-n FISH_COUNT] [-t [DURATION]]  
               [-T [DIRECTION]] [-bl [ACTION]]  
               [opts ...]  

啟動《俄羅斯釣魚4》自動腳本  

位置參數:  
  opts                  覆寫配置文件參數  

選項:  
  -h, --help            顯示幫助信息  
  -c, --coffee          體力不足時飲用咖啡  
  -A, --alcohol         定期飲用酒精飲料後存魚  
  -r, --refill          通過茶和胡蘿蔔補充飢餓與舒適度  
  -H, --harvest         拋竿前自動收餌  
  -g, --gear_ratio      超時後切換齒輪比  
  -f, --friction_brake  啟用自動摩擦剎車  
  -l, --lift            遛魚時持續提竿  
  -C, --skip_cast       跳過首次拋竿直接收線  
  -o, --spod_rod        定期重拋餌料竿  
  -L, --lure            定期隨機更換擬餌（僅路亞模式）  
  -x, --mouse           拋竿前隨機移動鼠標  
  -X, --pause           定期暫停腳本運行  
  -b, --bite            拋竿後截圖保存至screenshots/（用於魚點分析）  
  -S, --screenshot      為每條捕獲的魚截圖保存  
  -e, --email           腳本停止後發送郵件通知  
  -P, --plot            在/logs目錄保存釣魚數據  
  -M, --miaotixing      腳本停止後發送喵提醒通知  
  -s, --shutdown        腳本停止後關閉電腦  
  -so, --signout        退出遊戲而非關閉  
  -gb, --groundbait     補充底餌（僅底釣模式）  
  -dm, --dry_mix        補充乾混合餌（僅底釣模式）  
  -pva, --pva           補充PVA餌（僅底釣模式）  
  -E, --electro         為Electro Raptor系列捲線器啟用電動模式  
  -a, --all             保留所有魚獲（默認）  
  -m, --marked          僅保留標記魚獲  
  -d, --default-spool   使用默認線軸圖標檢測收線（默認）  
  -R, --rainbow-line    使用彩虹線計量器檢測收線  
  -p PID, --pid PID     指定配置檔ID  
  -N PROFILE_NAME, --pname PROFILE_NAME  
                        指定配置檔名稱  
  -n FISH_COUNT, --fishes-in-keepnet FISH_COUNT  
                        魚護當前魚量（默認0）  
  -t [DURATION], --boat-ticket [DURATION]  
                        自動續費船票，時長：'1','2','3'或'5'小時（默認5小時）  
  -T [DIRECTION], --trolling [DIRECTION]  
                        啟用拖釣模式，方向：'forward','left','right'（默認按'j'前進）  
  -bl [ACTION], --broken-lure [ACTION]  
                        斷餌自動處理，操作：'replace'或'alarm'（默認更換）  
```  

> [!TIP]  
> 其他工具如`craft.py`或`move.py`也支持`-h`參數顯示幫助信息。  

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
組合底釣配置與`-j`參數實現：  
```  
python tools\main.py -j KEY.BOTTOM_RODS "1, 2"  # 指定使用1、2號快捷鍵位  
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
_C.KEEPNET.DELAY = 0.0  # 存魚前延遲（用於截圖）  
_C.KEEPNET.FULL_ACTION = "quit"  # 滿護操作：quit（退出）/alarm（警報）
# -m模式保留魚種
# 選項: mackerel, saithe, herring, squid, scallop, mussel
_C.KEEPNET.RELEASE_WHITELIST = (  # -m模式保留魚種  
    "mackerel", "saithe", "herring",  
    "squid", "scallop", "mussel"  
)
# 魚種保留黑名單
# 選項: perch, shorthorn sculpin
_C.KEEPNET.BLACKLIST = (
)

# ----------------------------- 通知設置 -------------------------------- #  
_C.NOTIFICATION = CN()  
_C.NOTIFICATION.EMAIL = "email@example.com"  # 郵箱地址  
_C.NOTIFICATION.PASSWORD = "password"  # 郵箱密碼  
_C.NOTIFICATION.SMTP_SERVER = "smtp.gmail.com"  # SMTP服務器  
_C.NOTIFICATION.MIAO_CODE = "example"  # 喵提醒識別碼  

# ----------------------------- 暫停設置（需-X參數）------------------------ #  
_C.PAUSE = CN()  
_C.PAUSE.DELAY = 1800  # 暫停間隔（秒）  
_C.PAUSE.DURATION = 600  # 暫停時長（秒）  

# ----------------------------- 配置檔詳解 -------------------------------- #  
_C.PROFILE = CN()  

## 路亞配置 ##  
_C.PROFILE.SPIN = CN()  
_C.PROFILE.SPIN.MODE = "spin"  
_C.PROFILE.SPIN.CAST_POWER_LEVEL = 5.0  # 拋投力度等級（1~5級，5為全力拋投）  
_C.PROFILE.SPIN.CAST_DELAY = 6.0  # 拋竿後等待時間（秒）  
_C.PROFILE.SPIN.TIGHTEN_DURATION = 0.0  # 收緊釣線時長（秒）  
_C.PROFILE.SPIN.RETRIEVAL_DURATION = 0.0  # 收線/提竿持續時間（秒）  
_C.PROFILE.SPIN.RETRIEVAL_DELAY = 0.0  # 收線後延遲（秒）  
_C.PROFILE.SPIN.PRE_ACCELERATION = False  # 拋竿前按住Shift（特殊技法）  
_C.PROFILE.SPIN.POST_ACCELERATION = "off"  # 遛魚時加速模式（on/off/auto）  
_C.PROFILE.SPIN.TYPE = "normal"  # 操作類型：normal（常規）/pause（停頓）/lift（提拉）  

## 底釣配置 ##  
_C.PROFILE.BOTTOM = CN()  
_C.PROFILE.BOTTOM.MODE = "bottom"  
_C.PROFILE.BOTTOM.CAST_POWER_LEVEL = 5.0  # 拋投力度  
_C.PROFILE.BOTTOM.CAST_DELAY = 4.0  # 拋竿後等待時間（秒）  
_C.PROFILE.BOTTOM.POST_ACCELERATION = "off"  # 遛魚加速模式  
_C.PROFILE.BOTTOM.CHECK_DELAY = 32.0  # 檢查咬口間隔（秒）  
_C.PROFILE.BOTTOM.CHECK_MISS_LIMIT = 16  # 最大空竿次數後重拋  

## 海釣/維基配置（Pirk技法）##  
_C.PROFILE.PIRK = CN()  
_C.PROFILE.PIRK.MODE = "pirk"  
_C.PROFILE.PIRK.CAST_POWER_LEVEL = 1.0  # 拋投力度（淺拋）  
_C.PROFILE.PIRK.CAST_DELAY = 4.0  # 拋竿後等待時間（秒）  
_C.PROFILE.PIRK.SINK_TIMEOUT = 60.0  # 餌沉底超時（秒）  
_C.PROFILE.PIRK.TIGHTEN_DURATION = 1.0  # 收線緊繃時長（秒）
_C.PROFILE.PIRK.DEPTH_ADJUST_DELAY = 4.0  # 調整深度延遲（秒）  
_C.PROFILE.PIRK.DEPTH_ADJUST_DURATION = 1.0 # 調整深度後的收線時長（秒）
_C.PROFILE.PIRK.CTRL = False  # 抽竿時按住Ctrl  
_C.PROFILE.PIRK.PIRK_DURATION = 0.5  # 抽竿時長（秒）  
_C.PROFILE.PIRK.PIRK_DELAY = 2.0  # 抽竿後延遲（秒）  
_C.PROFILE.PIRK.PIRK_TIMEOUT = 32.0  # 抽竿超時（秒）  
_C.PROFILE.PIRK.PIRK_RETRIEVAL = False  # 抽竿時收線  
_C.PROFILE.PIRK.HOOK_DELAY = 0.5  # 中魚後檢查延遲（秒）  
_C.PROFILE.PIRK.POST_ACCELERATION = "auto"  # 遛魚加速模式 

## 升降釣法配置（深海升降釣組）##  
_C.PROFILE.ELEVATOR = CN()  
_C.PROFILE.ELEVATOR.MODE = "elevator"  
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
_C.PROFILE.BOLOGNESE.CAST_POWER_LEVEL = 5.0  # 拋投力度  
_C.PROFILE.BOLOGNESE.CAST_DELAY = 4.0  # 拋竿後等待時間（秒）  
_C.PROFILE.BOLOGNESE.FLOAT_SENSITIVITY = 0.68  # 浮標檢測敏感度  
_C.PROFILE.BOLOGNESE.DRIFT_TIMEOUT = 32.0  # 漂流超時重拋（秒）  

def get_cfg_defaults():  
    """獲取默認配置節點"""  
    return _C.clone()  
```  

[Configuration guide]: /docs/CONFIGURATION.md