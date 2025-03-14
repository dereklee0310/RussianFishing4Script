作者很懶，直接把丟給DeepSeek R1生成🤗

**[[英文版]][README]**
<div align="center">

![RF4S][RF4S logo]
<h1 align="center">RF4S: 俄羅斯釣魚4腳本</h1>

**一個簡易的《俄羅斯釣魚4》輔助腳本，支持旋轉釣、底釣、海釣和浮標釣。**

<a target="_blank" href="https://opensource.org/license/gpl-3-0" style="background:none">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" style="height: 22px;" />
</a>
<a target="_blank" href="https://discord.gg/BZQWQnAMbY" style="background:none">
    <img src="https://img.shields.io/badge/discord-加入討論-rf44.svg?labelColor=191937&color=6F6FF7&logo=discord" style="height: 22px;" />
</a>
<a target="_blank" href="http://makeapullrequest.com" style="background:none">
    <img src="https://img.shields.io/badge/PRs-歡迎提交-brightgreen.svg?style=flat" style="height: 22px;" />
</a>
<a target="_blank" href="https://github.com/pylint-dev/pylint" style="background:none">
    <img src="https://img.shields.io/badge/代碼檢查-pylint-yellowgreen" style="height: 22px;" />
</a>
<a target="_blank" href="https://github.com/psf/black" style="background:none">
    <img src="https://img.shields.io/badge/代碼風格-black-000000.svg" style="height: 22px;" />
</a>
<!-- <a target="_blank" href="link_to_docs, tbd" style="background:none">
    <img src="https://img.shields.io/badge/文檔-%23BE1B55" style="height: 22px;" />
</a> -->  

![Python badge][Python badge]
![Windows badge][Windows badge]

</div>

> [!TIP]
> 如需建議新功能、報告錯誤或獲取腳本使用幫助，請加入 [Discord 伺服器][Discord]。


## 快速開始  
### 環境準備
下載並安裝 **[Python 3.12][Python]**。  

> [!IMPORTANT] 
> 安裝時請務必勾選「將 Python 加入環境變數」（`Add to PATH`）。

> [!WARNING] 
> 不支持 Python 3.13 及以上版本。

### 安裝步驟
1. 打開命令提示符（cmd）或 PowerShell
2. 克隆倉庫並進入項目目錄：
```
git clone https://github.com/dereklee0310/RussianFishing4Script.git
cd RussianFishing4Script
```
> [!TIP]
> 若未安裝 git，可直接 **[下載倉庫壓縮包][Download]** 並解壓。

> [!WARNING] 
> 項目路徑請勿包含非英文字符。

### 依賴安裝
運行安裝腳本以安裝依賴包並生成默認配置文件：
```
setup.bat
```

> [!TIP] 
> 若已安裝 Python 其他版本，建議創建虛擬環境以避免依賴衝突。

### 遊戲設置
- 在 Windows 滑鼠設置中啟用 **[點擊鎖定][Clicklock]**，並將鎖定時間設為「長」
- 確保遊戲語言與 `config.yaml` 中的設置一致（默認為 `EN`）
- 將遊戲界面縮放設為 `1x`
- 遊戲顯示模式設為 `窗口模式` 或 `無邊界窗口`
- 確保魚線已完全纏繞，或使用彩虹線並添加 `-R` 參數
- 如需使用 `-r` 或 `-c` 參數，請將茶、胡蘿蔔和咖啡加入 **[快捷食物欄][Favorite food]**
- 若需自動更換釣具，請將相關物品加入 **[快捷釣具欄][Favorite lure]**

## 使用方法
### 開始前準備...
- 運行腳本前，請先將角色移動至釣點
- 路亞/海釣/浮子/維基釣法：手持對應魚竿
- 底釣模式：
    - 將釣組添加至快捷欄（1 ~ 3 號位）
    - 拋竿後將釣組放置在角色附近，以便腳本通過快捷鍵操作
> [!NOTE]
> 目前僅底釣模式支持多竿操作。

### 運行腳本！
使用默認配置運行腳本：
```
python tools\main.py
```
高級用法請參閱 **[配置指南][Configuration guide]**。
> [!IMPORTANT]
> 若在新終端窗口中運行，請先切換至項目目錄：
> ```
> cd "你的項目路徑\RussianFishing4Script"
> ```

> [!NOTE]
> 魚護滿後腳本會自動停止，手動停止請在終端中輸入 `Ctrl-C`。 

## 工具集
### 自動製作
**持續製作直至材料耗盡（按 `Ctrl-C` 退出）：**
```
python tools\craft.py
```
**製作 10 個物品：**
```
python tools\craft.py -n 10
```
**丟棄已製作的地面餌料：**
```
python tools\craft.py -d
```
> [!IMPORTANT]
> 運行前請先選中所需材料。
### 自動收餌
**持續收餌（按 `Ctrl-C` 退出）：**
```
python tools\harvest.py
```
**收餌時自動補充飢餓和舒適度：**
```
python tools\harvest.py -r
```
**等待時打開控制面板（降低功耗）：**
```
python tools\harvest.py -s
```
### 自動移動
**啟用自動前進（按 `W` 暫停，`S` 退出）：**
```
python tools\move.py
```
**按住 Shift 移動：**
```
python tools\move.py -s
```

### 摩擦剎車自動化
**自動控制摩擦剎車（按 `G` 重置，`H` 退出）：**
```
python tools\auto_friction_brake.py
```

### 釣具數值計算
**根據磨損顯示捲線器的真實阻力與前導線實際負載：**
```
python tools\calculate.py
```

## 配置說明
詳見 **[配置指南][Configuration guide]**。

## MIAO_CODE如何配置?
1. 關注微信公衆號 **[喵提醒][Miaotixing]**。
   
2. 新建提醒服務  
<img src="../static/readme/mtx1.png" height="400">
<img src="../static/readme/mtx2.png" height="400">

3. 效果展示  
<img src="../static/readme/mtx3.png" height="400">

[Miaotixing]: https://miaotixing.com/how

## 故障排除
<details>
<summary>如何停止腳本？</summary>

- 在終端中輸入 `Ctrl-C`。 
</details>
<!-- ------------------------------- 分隔線 -------------------------------- -->
<details>
<summary>無法停止腳本？</summary>

- 可能按鍵被鎖定（如 `Ctrl`、`Shift`、滑鼠按鍵等），  
  再次按下對應按鍵解鎖後，輸入 `Ctrl-C` 即可。
</details>
<!-- ------------------------------- 分隔線 -------------------------------- -->
<details>
<summary>卡在 128% 拋竿？</summary>

- 檢查遊戲語言與腳本語言設置是否一致
- 確保魚線已完全纏繞，或使用彩虹線並添加 `-R` 參數
</details>

<!-- ------------------------------- 分隔線 -------------------------------- -->
<details>
<summary>收線完成後未提竿？</summary>

- 確保魚線已完全纏繞，或使用彩虹線並添加 `-R` 參數
- 調整遊戲窗口大小
- 降低 `config.yaml` 中的 `SPOOL_CONFIDENCE` 數值
- 遠離光源或關閉船燈
</details>
<!-- ------------------------------- 分隔線 -------------------------------- -->
<details>
<summary>腳本運行但無反應？</summary>

- 以管理員身份打開新終端窗口並重新運行
</details>
<!-- ------------------------------- 分隔線 -------------------------------- -->

## 更新日誌
詳見 **[更新日誌][Changelog]**。

## 許可協議
**[GNU 通用公共許可協議第三版][License]**

## 參與貢獻
歡迎提交代碼、報告錯誤或提出新功能建議。

## 聯繫作者
dereklee0310@gmail.com 

[RF4S logo]: /static/readme/RF4S.png
[Python badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Windows badge]: https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white

[README]: /README.md
[Discord]: https://discord.gg/BZQWQnAMbY
[Python]: https://www.python.org/downloads/
[Download]: https://github.com/dereklee0310/RussianFishing4Script/archive/refs/heads/main.zip
[Clicklock]: /static/readme/clicklock.png
[Favorite food]: /static/readme/favorites.png
[Favorite lure]: /static/readme/favorites_2.png
[Configuration guide]: /docs/CONFIGURATION.md
[Changelog]: /docs/CHANGELOG.md

[License]: /LICENSE