**[[English version]][readme]**
<div align="center">

![RF4S][rf4s_logo]
<h1 align="center">RF4S：Russian Fishing 4 Script</h1>

**俄羅斯釣魚4自動釣魚機器人，支援路亞、水底、海釣、維基釣組及手竿等模式。**

<a target="_blank" href="https://opensource.org/license/gpl-3-0" style="background:none">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" style="height: 22px;" />
</a>
<a target="_blank" href="https://discord.gg/BZQWQnAMbY" style="background:none">
    <img src="https://img.shields.io/badge/discord-join-rf44.svg?labelColor=191937&color=6F6FF7&logo=discord" style="height: 22px;" />
</a>
<a target="_blank" href="http://makeapullrequest.com" style="background:none">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat" style="height: 22px;" />
</a>
</a>
<a target="_blank" href="https://www.python.org/downloads/" style="background:none">
    <img src="https://img.shields.io/badge/python-3.10_%7C_3.11_%7C_3.12-blue
    " style="height: 22px;" />
</a>
<a target="_blank" href="https://github.com/astral-sh/ruff" style="background:none">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    " style="height: 22px;" />


</div>

> [!TIP]
> 如果您想建議新功能、回報錯誤或尋求使用幫助，請加入我們的 [Discord 伺服器][discord]。


## 安裝
> [!WARNING] 
> 下載路徑不能包含非英文字符。
### 可執行檔
從 [Releases][releases] 下載 `rf4s.zip`。  
### pip
```
git clone https://github.com/dereklee0310/RussianFishing4Script.git
cd RussianFishing4Script
pip install -r requirements.txt
```
> [!IMPORTANT] 
> 不支援 Python 3.13+，支援版本：>=3.10, <=3.12。
### uv
```
git clone https://github.com/dereklee0310/RussianFishing4Script.git
cd RussianFishing4Script
uv sync
```
> [!WARNING] 
> 路徑不可包含非英文字符。


## 設定
### Windows 滑鼠按住鎖定
若啟用了 Windows 滑鼠按住鎖定功能，請將時間設定為長。

![click_lock]
### 顯示設定
請將系統與遊戲內的介面縮放比例都設定為「1x」，並使用「視窗模式」或「無邊框視窗模式」作為遊戲視窗模式。
### 線軸偵測
預設情況下，機器人會監控線軸（紅框）以偵測收線進度。  
請確保線軸已完全纏繞釣線，以精確判斷收線完成。  
若您使用彩虹線，請啟用 `-R` 參數，切換至儀表（綠框）進行偵測，以獲得更佳精度。  
詳情請參閱 **[CONFIGURATION][configuration]** 了解如何使用。

![status]

## 使用方式
### 水底
將您的釣竿加入快速選擇欄位，拋投並放置在附近，以便機器人能透過快捷鍵（1～3）存取。  
### 路亞、海釣、手竿等
拿起您想使用的釣竿。
> [!NOTE]
> 目前僅水底模式支援多根釣竿。

### 可執行檔
雙擊執行，或使用：
```
.\main.exe
```
#### Python
```
python main.py
```
### uv
```
cd "專案路徑"
uv run main.py
```

> [!TIP]
> 請參閱 **[CONFIGURATION][configuration]** 以了解進階使用與設定選項。

## 功能
| 功能                     | 說明                                              |
| ------------------------ | ------------------------------------------------ |
| 釣魚機器人               | 自動釣魚機器人                                     |
| 製作物品                 | 自動製作餌料、誘餌、假餌等                         |
| 向前移動                 | 切換按下 `W`（或 `Shift + W` 快速前進）            |
| 自動挖餌                 | 掛機並自動採集餌料                                 |
| 自動調整摩擦             | 自動調整捲線器的摩擦                               |
| 計算釣具屬性             | 計算釣具的屬性與建議使用的摩擦                     |

## 常見問題排除
<details>
<summary>Windows Defender 將其偵測為惡意軟體？</summary>

- 屬於誤判，請見 [此處][malware]。 
</details>

<details>
<summary>無法停止腳本？</summary>

- 可能某些按鍵仍處於按下狀態（例如 `Ctrl`、`Shift`、滑鼠按鈕等）。  
  請再次按下這些按鍵以釋放，然後正常輸入 `Ctrl-C` 即可。
</details>

<details>
<summary>卡在拋投 12x%？</summary>

- 請確認遊戲語言與腳本語言設定相同。
- 確保您的捲線器已完全纏繞釣線，或裝備彩虹線並使用 `-R` 參數。 
</details>

<details>
<summary>收線完成後未舉竿？</summary>

- 確保您的捲線器已完全纏繞釣線，或裝備彩虹線並使用 `-R` 參數。 
- 調整遊戲視窗大小。
- 降低 `config.yaml` 中 `BOT.SPOOL_CONFIDENCE` 的數值。
- 避免強光來源（如陽光直射）或關閉船上燈光。
</details>

<details>
<summary>機器人正在運行但無反應？</summary>

- 請以系統管理員身分執行。
</details>

## 更新日誌
詳見 **[CHANGELOG][changelog]**。

## 授權條款
**[GNU General Public License version 3][license]**

## 貢獻
歡迎任何形式的貢獻、錯誤回報或新功能建議。

## 聯絡我
dereklee0310@gmail.com 

[readme]: /README.md
[rf4s_logo]: /static/readme/RF4S.png
[python_badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[windows_badge]: https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white
[click_lock]: /static/readme/clicklock.png
[malware]: https://nuitka.net/user-documentation/common-issue-solutions.html#windows-virus-scanners

[discord]: https://discord.gg/BZQWQnAMbY  
[python]: https://www.python.org/downloads/  
[releases]: https://github.com/dereklee0310/RussianFishing4Script/releases  
[status]: /static/readme/status.png
[configuration]: /docs/en/CONFIGURATION.md
[changelog]: /docs/en/CHANGELOG.md
[license]: /LICENSE