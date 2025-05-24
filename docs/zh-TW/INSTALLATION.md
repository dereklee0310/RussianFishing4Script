**[[English version]][installation]**
# 安裝指南
## 必要條件
下載並安裝 **[Python 3.12.*][Python]**。  

> [!IMPORTANT]  
> 安裝時請務必勾選 **「Add Python to PATH」** 選項。  

> [!WARNING]  
> 不支援 Python 3.13 及以上版本。

## 安裝步驟
### 方法一：透過 Git 克隆
```
git clone https://github.com/dereklee0310/RussianFishing4Script.git
cd RussianFishing4Script
.\setup.bat
```
> [!IMPORTANT]  
> 系統必須已安裝 Git。
### 方法二：手動下載
1. [下載此儲存庫][download]。
2. 對 `RussianFishing4Script-main.zip` 按右鍵並選擇「解壓縮到當前位置」。
3. 開啟解壓後的資料夾 (`RussianFishing4Script-main`)，雙擊 `setup.bat` 以安裝依賴項。
> [!TIP] 
> 若已安裝 Python 其他版本，建議創建虛擬環境以避免依賴衝突。

> [!WARNING]  
> 下載路徑不得包含非英文字元。

## 環境設定
### 啟用滑鼠點擊鎖定
- 前往 Windows 滑鼠設定 > 啟用 **[滑鼠點擊鎖定][clicklock]**。
- 將鎖定前的時間設為「長」。
### 語言設定
- 確認遊戲語言與 `config.yaml` 中的語言設定一致（預設為 "EN"）。
### 顯示設定
- 將系統和遊戲內的介面縮放比例均設為「1x」。
- 遊戲視窗模式請使用「視窗模式」或「無邊框視窗」。
### 線軸偵測
- 預設情況下，機器人會檢查線軸（紅色框）狀態以判斷收線是否完成。  
  線軸必須裝滿線，機器人才能判斷收線是否結束。
- 若裝備彩虹釣線，請使用 `-R` 選項改為偵測線的米數（綠色框）以獲得更佳準確度。
- 請參閱 [設定指南][configuration] 瞭解如何使用啟動選項。
  
![status]

[installation]: /docs/en/INSTALLATION.md
[download]: https://github.com/dereklee0310/RussianFishing4Script/archive/refs/heads/main.zip
[configuration]: /docs/zh-TW/CONFIGURATION.md
[clicklock]: /static/readme/clicklock.png
[status]: /static/readme/status.png