**[[English version]][readme]**
<div align="center">

![rf4s_logo]
<h1 align="center">RF4S: 俄羅斯釣魚4腳本</h1>

**俄羅斯釣魚4的簡易釣魚機器人，支援路亞、水底、海釣及手竿等模式。**

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
> 若想建議新功能、回報錯誤或取得使用幫助，請加入 [Discord 伺服器discordDiscord]。


## 快速入門
### 必要條件
下載並安裝 **[Python 3.12.*][python]**。  

> [!IMPORTANT]  
> 安裝時請務必勾選 **「將Python加入PATH」** 選項。  

> [!WARNING]  
> 不支援 Python 3.13 及以上版本。
### 安裝步驟
請參閱 **[安裝指南][installation]**。
## 使用方式
### 開始前注意事項...
- 執行腳本前，請先將角色移動至釣點
- 路亞/海釣/手竿/維基模式：手持要使用的釣竿。
- 底釣模式：
    - 將釣組添加至快捷欄位。
    - 拋竿後將釣竿放置在附近，以便腳本可透過快捷鍵（1 ~ 3）操作。
> [!NOTE]
> 目前僅底釣模式支援多竿操作。

### 開始執行！
1. 開啟 cmd/PowerShell
2. 進入專案目錄並執行腳本（按 `CTRL-C` 退出）：
```
cd "專案目錄路徑"
python tools\main.py
```
> [!TIP]
> `專案目錄路徑` 是克隆或解壓縮專案後存放檔案的目錄。  
> ![路徑示意][path]

> [!TIP]
> 進階設定和使用方式請參閱 **[設定指南][configuration]**。

## 工具集
### 製作物品
執行前選取材料，按 `Ctrl-C` 退出。
```
python tools\craft.py
```
### 自動挖餌
按 `Ctrl-C` 退出。
```
python tools\harvest.py
```
### 自動前進
按 `W` 暫停，按 `S` 退出。
```
python tools\move.py
```
### 自動調整摩擦
按 `G` 重置，按 `H` 退出。
```
python tools\auto_friction_brake.py
```
### 計算釣組數值與摩擦
```
python tools\calculate.py
```

## 疑難排解
<details>
<summary>如何停止腳本？</summary>

- 在終端機中輸入 `CTRL-C`。 
</details>
<!-- ------------------------------- 分隔線 -------------------------------- -->
<details>
<summary>無法停止腳本？</summary>

- 可能按鍵被卡住（如 `CTRL-C`、`SHIFT`、滑鼠按鍵等），  
  重新按壓卡住的按鍵後，再輸入 `CTRL-C`。
</details>
<!-- ------------------------------- 分隔線 -------------------------------- -->
<details>
<summary>拋竿卡在128%？</summary>

- 確認遊戲語言與腳本語言設定一致。
- 確保線軸已纏滿釣線，或裝備彩虹線並使用 `-R` 參數。 
</details>

<!-- ------------------------------- 分隔線 -------------------------------- -->
<details>
<summary>收線完成後未抬竿？</summary>

- 確保線軸已纏滿釣線，或裝備彩虹線並使用 `-R` 參數。 
- 調整遊戲視窗大小。
- 降低 `config.yaml` 中的 `SPOOL_CONFIDENCE` 數值。
- 遠離光源或關閉船燈。
</details>
<!-- ------------------------------- 分隔線 -------------------------------- -->
<details>
<summary>腳本執行但無反應？</summary>

- 以系統管理員身份開啟 cmd/Powershell 並重新執行。
</details>
<!-- ------------------------------- 分隔線 -------------------------------- -->

## 更新日誌
詳見 **[更新日誌][changelog]**。

## 授權條款
**[GNU General Public License version 3][license]**

## 貢獻指南
歡迎提交錯誤報告、功能建議或任何形式的貢獻。

## 聯絡作者
dereklee0310@gmail.com 

[readme]: /README.md

[rf4s_logo]: /static/readme/RF4S.png
[python_badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[windows_badge]: https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white

[discord]: https://discord.gg/BZQWQnAMbY
[python]: https://www.python.org/downloads/
[installation]: /docs/zh-TW/INSTALLATION.md
[configuration]: /docs/zh-TW/CONFIGURATION.md
[changelog]: /docs/zh-TW/CHANGELOG.md
[path]: /static/readme/path.png
[license]: /LICENSE