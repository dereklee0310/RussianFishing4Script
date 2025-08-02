**[[English version]][configuration]**
## 啟動選項
你可以使用啟動選項在程式啟動時啟用一項或多項功能。
### 執行檔
```
.\main.exe ...
```
### Python
```
python main.py ...
```
### uv
```
uv run main.py ...
```
> [!NOTE]
> 如果未提供任何啟動選項，或透過雙擊執行，你可以在選擇要使用的功能後再輸入。
>
> ![啟動選項][launch_options]

### 範例（執行檔）
#### 使用「釣魚機器人」並設定護網中的魚數量為 32（需捕獲 68 條魚）：
```
.\main.exe bot -n 32
```
#### 使用「釣魚機器人」，選擇第 3 個設定檔，釣魚時飲用咖啡，並在停止時寄送電子郵件通知自己：
```
.\main.exe bot -p 3 -c --email
```
#### 使用「釣魚機器人」，消耗胡蘿蔔、茶與咖啡來補充角色狀態，並在拋竿前盡可能採集餌料：
```
.\main.exe bot -rcH
```
#### 使用「製作物品」功能來製作 10 個物品：
```
.\main.exe craft -n 10
```
#### 使用「計算釣具屬性」功能：
```
.\main.exe cal
```


> [!TIP]
> 使用 `-h` 可查看幫助訊息。

> [!IMPORTANT]
> 若想使用 `-r` 或 `-c` 選項，請務必先將茶、胡蘿蔔／咖啡加入你的 **[最愛食物][favorite_food]**。  
> 若要使用會自動替換物品的選項，也需將相關物品加入你的 **[最愛餌料][favorite_lure]**。

## 設定配置
### 設定修改
請在 [`config.yaml`][config.yaml] 中編輯你的設定，重新啟動後變更才會生效。  
設定參考請見 [`default.py`][default.py]。

### 新增設定檔
複製預設設定檔中的現有設定檔，進行編輯後，加入 `PROFILE` 區段中。

以下範例新增一個名為 `MY_BOTTOM_FISHING` 的設定檔，重新啟動後將會出現在設定檔清單中：
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
    DESCRIPTION: "我的底釣模式。"
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
> 若需使用 `-r` 或 `-c` 參數，請將茶和胡蘿蔔/咖啡加入 **[收藏物品][favorite_food]**。  
> 需自動更換物品的功能，請將相關物品加入 **[收藏物品][favorite_lure]**。

### 覆寫設定  
有時你可能只想暫時變更 [`config.yaml`][config.yaml] 中的某個設定而不修改設定檔，
這時可透過啟動選項達成。以下為一個簡單範例，用來覆寫語言設定：
```  
.\main.exe LANGUAGE "ru"
```  

### 雙竿拖釣模式  
由於船上拖釣本質上就是按住拖釣鍵與方向鍵的底釣，
因此你可以將底釣設定檔搭配 -T 參數使用。
由於船上沒有第三支竿架，你應該像這樣覆寫底釣竿的按鍵設定：  
```  
.\main.exe bot -T KEY.BOTTOM_RODS "(1, 2)"
```  


## 喵提醒的MIAO_CODE配置方式
1. 關注微信公衆號 **[喵提醒][meow]**。
   
2. 新建提醒服務  
![meow_1] ![meow_2]

3. 效果展示  
![meow_3]

[launch_options]: /static/readme/launch_options.png
[path]: /static/readme/path.png
[config.yaml]: /rf4s/config/config.yaml
[default.py]: /rf4s/config/defaults.py
[configuration]: /docs/en/CONFIGURATION.md
[favorite_food]: /static/readme/favorite_food.png
[favorite_lure]: /static/readme/favorite_lure.png
[meow]: https://miaotixing.com/how
[meow_1]: /static/readme/mtx1.png
[meow_2]: /static/readme/mtx2.png
[meow_3]: /static/readme/mtx3.png