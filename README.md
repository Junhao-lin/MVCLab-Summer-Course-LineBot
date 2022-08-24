# LineBot
## How to use
1. Install Python Package
  ```
  pip install -r requirements.txt
  ```
2. Install InfluxDB
```
  sudo curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
  sudo echo "deb https://repos.influxdata.com/ubuntu bionic stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
  sudo apt update
  sudo apt install influxdb
```
3. Run ngrok
```
  uvicorn sport:app --reload
```
4. Test LineBot 
```
  python main.py
```
## Indtroduction
### Calculator
  - operator
    - `+`
    - `-`
    - `*`
    - `/`
  - input (a,b can be negative)
    - `a+b`
    - `a + b`
    - `a+b =` 
  - output
    - `calculation result` 
    - If you enter illegal characters or don't match the rules you will get the picture

### Accounting

  - `#note [事件] [+/-] [錢]`                     -> 新增記帳資料
  - `#report`                                    -> 顯示目前記帳資料
  - `#delete [i]`                                -> 刪除第i筆資料
  - `#drop`                                      -> 刪除全部資料
  - `#sum`                                       -> 結算一天前的帳