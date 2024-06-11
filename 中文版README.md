<div align="center">

![RF4S](static/readme/RF4S.png)
<h1 align="center">RF4S</h1>

**俄釣4釣魚腳本，支持手竿、水底、路亞以及海釣模式**

<a target="_blank" href="https://opensource.org/license/gpl-3-0" style="background:none">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" style="height: 22px;" />
</a>
<a target="_blank" href="https://discord.gg/BZQWQnAMbY" style="background:none">
    <img src="https://img.shields.io/badge/discord-join-rf44.svg?labelColor=191937&color=6F6FF7&logo=discord" style="height: 22px;" />
</a>
<a target="_blank" href="http://makeapullrequest.com" style="background:none">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat" style="height: 22px;" />
</a>
<a target="_blank" href="https://github.com/pylint-dev/pylint" style="background:none">
    <img src="https://img.shields.io/badge/linting-pylint-yellowgreen" style="height: 22px;" />
</a>
<a target="_blank" href="https://github.com/psf/black" style="background:none">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" style="height: 22px;" />
</a>
<!-- <a target="_blank" href="link_to_docs, tbd" style="background:none">
    <img src="https://img.shields.io/badge/docs-%23BE1B55" style="height: 22px;" />
</a> -->  

![python][Python badge]
![windows][Windows badge]
</div>

## [更新日誌][Release notes]
> [!TIP]
> 加入我們的 [Discord 伺服器][Discord] 以取得最新消息。

## 準備工作
### 前提
- [Python3.10+][Python]


### 安裝腳本
[下載][Download]此項目並解壓縮，或:
```
git clone https://github.com/dereklee0310/RussianFishing4Script
```

### 安裝依賴庫並初始化設定
```
cd "項目路徑"
.\setup.bat
```
> [!TIP]
> 如果你之前下載過Python，請建立一個新的虛擬環境以避免版本衝突。

## 使用方式
### 前提
- 啟用 **[滑鼠鎖定][Clicklock]**  並將按下時間設定為"長"
- 更改遊戲語言為英文
- 將遊戲縮放倍率設為"1x"
- 將遊戲視窗顯示模式設為"視窗化或"無邊框模式"
- 將線杯裝滿線，或是裝備彩虹線並在執行腳本時使用`-R`參數
- 把茶、咖啡和胡蘿蔔加到 **[最愛][Favorite food]**
- 如果想使用自動替換損壞擬餌的功能，請將用於替換的擬餌加到 **[最愛][Favorite lure]**
### 在啟動腳本前...
- 移動遊戲人物至釣點
- 手竿/路亞/海釣/維基釣組模式: 將釣竿拿在手上
- 水底模式: 將釣竿添加至快捷鍵 (1 ~ 3)，並在拋竿後將所有釣竿放置於腳色前方

> [!NOTE]
> 目前手竿及維基釣組模式只支援單竿作釣。

> [!IMPORTANT]
> 在使用手竿模式時，請將`config.ini`中的`window_size`設為你的遊戲視窗大小。

### 1. 變更當前工作目錄
```
cd "項目路徑"
cd src
```

### 2. 執行腳本
以下是一些範例:
- 以預設設定執行腳本
```
python app.py
```
> [!WARNING]
> 如果腳本沒有自動切換至遊戲視窗或是無動作，請使用管理者權限執行終端。
- 顯示幫助訊息 (參數使用教學)
```
python app.py -h
```
- 執行腳本，並將漁戶內魚的數量設為32 (腳本會在捕獲68條後結束)
```
python app.py -n 32
```
- 使用模式3，拉大魚時喝咖啡，並在腳本結束後寄一封通知到你的信箱
```
python app.py -p 3 --coffee --email
```
- 釋放未達標魚，自動補充飽食度和體溫，並繪製一張魚獲/時間關係圖
```
python app.py -mrP
```
### 命令行參數
- `-m`: 只保留達標魚
- `-c`: 跟魚纏鬥時自動喝咖啡補充體力
- `-A`: 定時喝酒
- `-r`: 在拋竿前自動消耗胡蘿蔔/茶補充飽食及體溫
- `-H`: 拋竿前自動挖餌，僅適用於水底模式
- `-e`: 執行完畢後寄信通知用戶，需配置郵箱相關設定
- `-P`: 繪製魚獲/時間關係圖並保存於logs/資料夾
- `-s`: 執行完畢後自動關機
- `-l`: 中魚後收線時頻繁抬桿
- `-g`: 自動切換傳送比
- `-R`: 使用彩虹線米數偵測是否收線完畢
- `-S`: 上魚後截圖並儲存至`screenshots/`資料夾
- `-n 數量`: 指定當前漁戶內的魚數量以便在滿戶時自動退出，預設為0
- `-p 模式id`: 指定欲使用的模式id
## 其他腳本
### 開啟/關閉前進模式
- 執行後自動按住W鍵控制腳色前進，按w暫停，按s退出
```
python move.py
```

### 製作物品
- 可搭配`-n 數量`參數指定欲製作的物品數量，預設為材料用完後停止
- 使用`-d`即可丟棄所有製作的物品，用於沖技能
```
python craft.py
```
> [!IMPORTANT]
> 請選擇欲製作的物品，材料和工具後再執行腳本

### 計算釣組可用的最大摩擦
- 根據提示輸入釣組參數即可
```
python calculate.py
```

### 原地掛機自動挖餌+自動補充體力
- 使用`-s`以在等待間隔切換至設定介面，節省不必要的畫面渲染
- `-n 秒數`可以自定義等待間隔的時間
```
python harvest.py
```

## 腳本設定
- **[視頻教程(舊)][Video]**
- 請參考 **[中文版template.ini][Template]** 中的說明, 並在 **[config.ini][Config]** 中修改設定。
- 你可以在 **[config.ini][Config]** 中修改`language`以變更語言，
  並根據 **[圖片添加指南][Integrity guide]** 添加缺失的圖片
- 欲使用郵件功能的話，請在`.env`中配置郵箱以及SMTP伺服器等資訊

## 疑難排解
**如何停止腳本運行?**
- 在終端輸入`Ctrl + C`.
   
**無法退出?**
- Shift鍵可能被腳本按下了，再按一次將其鬆開後即可正常退出

**收線卡住了?**
- 將線杯裝滿，或使用`-R`參數以及彩虹主線
- 更改遊戲視窗大小
- 降低`config.ini`中`retrieval_detect_confidence`的值
- 遠離光源(e.g, 露營燈、船燈)

## 授權條款
[GNU General Public License version 3][license]

## 貢獻
如果你覺得這個腳本有幫助到你的話，請給這個repo一個星星 :)  
歡迎任何形式的貢獻，包含但不限於bug回報、功能建議、PR

## 聯繫方式
### Email
dereklee0310@gmail.com
### WeChat
<img src="static/readme/wechat.jpg" width="240">

[RF4S logo]: static/readme/RF4S.png

[Python badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Windows badge]: https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white

[Release notes]: release_notes.md
[Discord]: https://discord.gg/BZQWQnAMbY
[Python]: https://www.python.org/downloads/
[Download]: https://github.com/dereklee0310/RussianFishing4Script/archive/refs/heads/main.zip
[Clicklock]: /static/readme/clicklock.png
[Favorite food]: /static/readme/favorites.png
[Favorite lure]: /static/readme/favorites_2.png
[Video]: https://www.youtube.com/watch?v=znLBYoXHxkw
[Template]: 中文版template.ini
[Config]: config.ini
[Integrity guide]: integrity_guide.md

[license]: LICENSE