**[[English version]][readme]**
<div align="center">

![rf4s_logo]
<h1 align="center">RF4S: 俄羅斯釣魚4腳本</h1>

**俄羅斯釣魚4自動釣魚機器人，支援紡車、底釣、海釣、維基釣組及手竿等模式。**

<a target="_blank" href="https://opensource.org/license/gpl-3-0" style="background:none">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" style="height: 22px;" />
</a>
<a target="_blank" href="https://discord.gg/BZQWQnAMbY" style="background:none">
    <img src="https://img.shields.io/badge/discord-join-rf44.svg?labelColor=191937&color=6F6FF7&logo=discord" style="height: 22px;" />
</a>
<a target="_blank" href="http://makeapullrequest.com" style="background:none">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat" style="height: 22px;" />
</a>
<!-- <a target="_blank" href="https://github.com/pylint-dev/pylint" style="background:none">
    <img src="https://img.shields.io/badge/代碼檢查-pylint-yellowgreen" style="height: 22px;" />
</a>
<a target="_blank" href="https://github.com/psf/black" style="background:none">
    <img src="https://img.shields.io/badge/代碼風格-black-000000.svg" style="height: 22px;" />
</a> -->
<!-- <a target="_blank" href="link_to_docs, tbd" style="background:none">
    <img src="https://img.shields.io/badge/文件-%23BE1B55" style="height: 22px;" />
</a> -->  

![Python 標章][python_badge]
![Windows 標章][windows_badge]

</div>

> [!TIP]
> 若需建議新功能、回報錯誤或取得使用幫助，請加入我們的 [Discord 伺服器][discord]。


## 快速開始
### 環境需求
**[Python 3.12.*][python]** (若需直接執行原始碼而非可執行檔)。
> [!WARNING] 
> 不支援 Python 3.13 以上版本。

### 安裝
#### 可執行檔
從 [Releases][releases] 下載 `rf4s.zip` 並解壓縮。
#### Python 原始碼 (開發者適用)
```
git clone https://github.com/dereklee0310/RussianFishing4Script.git
cd RussianFishing4Script
.\setup.bat
```
> [!WARNING] 
> 路徑不可包含非英文字符。

### 環境設定
#### 語言
- 確認遊戲語言與 `config.yaml` 中的設定一致（預設為 "en"）。
#### 顯示設定
- 系統與遊戲介面縮放比例皆設為 "1x"。
- 遊戲視窗模式設為「視窗化」或「無邊框視窗。
#### 線杯偵測
- 預設透過線杯（紅框區域）偵測收線進度，請確保線杯已裝滿線以獲得準確偵測結果。
- 若使用彩虹線，請啟用 `-R` 參數切換至儀表板（綠框區域）偵測模式。
- 啟動參數說明詳見 **[配置說明][configuration]**。

![status]

## 使用方式
### 開始前準備...
#### 底釣模式
將釣竿加入快速選擇欄位，並在拋竿後置於附近，確保腳本能透過快捷鍵 (1~3) 操作。
#### 其他模式
拿起要使用的釣竿即可。
> [!NOTE]
> 目前僅底釣模式支援多竿操作。

### 開始執行！
#### 可執行檔
雙擊執行檔即可運行
#### Python 原始碼 (開發者適用)
```
cd "專案路徑"
python tools\main.py
```

> [!TIP]
> 進階用法請參閱 **[配置說明][configuration]**

## 功能列表
| 功能         | 說明                           |
| ------------ | ------------------------------ |
| 釣魚機器人   | 主腳本                         |
| 物品製作     | 自動製作物品                   |
| 自動挖餌     | 閒置並自動挖餌                 |
| 自動前進     | 自動按 `W` (或 `Shift+W` 衝刺) |
| 自動摩擦     | 自動調整摩擦                   |
| 釣具參數計算 | 計算釣組實際拉力/負載          |

## 疑難排解
<details>
<summary>如何停止腳本？</summary>

- 在終端機輸入 `Ctrl-C`。
</details>
<!-- ------------------------------- 分隔線 -------------------------------- -->
<details>
<summary>無法停止腳本？</summary>

- 可能因部分按鍵處於按下狀態 (如 `Ctrl`, `Shift`, 滑鼠按鍵等)，  
  重新按下對應按鍵釋放後，再輸入 `Ctrl-C`。
</details>
<!-- ------------------------------- 分隔線 -------------------------------- -->
<details>
<summary>拋竿卡在 12x%？</summary>

- 確認遊戲語言與腳本設定一致。
- 確保線杯已裝滿線，或使用彩虹線並啟用 `-R` 參數。
</details>
<!-- ------------------------------- 分隔線 -------------------------------- -->
<details>
<summary>收線完成後未提竿？</summary>

- 確保線杯已裝滿線，或使用彩虹線並啟用 `-R` 參數。
- 調整遊戲視窗大小。
- 降低 `config.yaml` 中的 `SPOOL_CONFIDENCE` 數值。
- 避免強光源直射（如陽光直射）或關閉船燈。
</details>
<!-- ------------------------------- 分隔線 -------------------------------- -->
<details>
<summary>腳本運行但無反應？</summary>

- 以系統管理員身分執行腳本。
</details>
<!-- ------------------------------- 分隔線 -------------------------------- -->

## 更新日誌
詳見 **[更新日誌][changelog]**。

## 授權條款
**[GNU General Public License version 3][license]**

## 貢獻指南
歡迎提交任何功能建議、錯誤回報或新功能構想。

## 聯絡方式
dereklee0310@gmail.com 

[readme]: /README.md
[rf4s_logo]: /static/readme/RF4S.png
[python_badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[windows_badge]: https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white

[discord]: https://discord.gg/BZQWQnAMbY
[python]: https://www.python.org/downloads/
[releases]: https://github.com/dereklee0310/RussianFishing4Script/releases
[status]: /static/readme/status.png
[configuration]: /docs/zh-TW/CONFIGURATION.md
[changelog]: /docs/zh-TW/CHANGELOG.md
[license]: /LICENSE