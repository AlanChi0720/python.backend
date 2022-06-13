# 初始會資料庫連線
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()
user= str(os.getenv("USER"))
password= str(os.getenv("PASSWORD"))
client= pymongo.MongoClient("mongodb+srv://"+user+":"+password+"@mycluster0.gcfkgiv.mongodb.net/?retryWrites=true&w=majority")
db= client.member_system

# 初始會 flask 伺服器
from flask import *
app= Flask(
    __name__,
    static_folder= "public",
    static_url_path= "/"
)
app.secret_key= "any string but secret"
# 處理路由 建立前端首頁
@app.route("/")
def index():
    return render_template("index.html") # !+tab 可產生基礎html格式
# 建立前端會員首頁
@app.route("/member")
def member():
    name= session["ID"]
    if "ID" in session:
        return render_template("member.html", name=name)
    else:
        return redirect("/")
# 建立前端錯誤首頁 /error?msg=錯誤訊息
@app.route("/error")
def error():
    message= request.args.get("msg", "發生錯誤，請聯繫客服")
    return render_template("error.html", message= message)
# 建立signup路由 (沒有前端，會將資料送往後端)
@app.route("/signup", methods=["POST"])
def signup():
    ID= request.form["ID"]
    email= request.form["email"]
    password= request.form["password"]
# 根據接收到的資料，跟資料庫互動
    collection= db.user
# 檢察是否有相同email的資料
    result= collection.find_one({
        "email":email
    })
    if result != None:
        return redirect("/error?msg=信箱已經被註冊")
    collection.insert_one({
       "ID":ID,
       "email":email,
       "password":password 
    })
    name= request.form["ID"]
    return render_template("signup.html" ,name= name)
# 建立login路由 (沒有前端，會將資料送往後端檢查)
@app.route("/login" , methods= ["POST"])
def login():
    # 從前端取得使用者資訊
    email= request.form["email"]
    password= request.form["password"]
    #和資料戶互動
    collection= db.user
    #檢查信箱、密碼是否正確
    result= collection.find_one({
        "$and":[
            {"email":email},
            {"password":password}
        ]
    })
    #找不到對應的資料: 登入失敗
    if result== None:
        return redirect("/error?msg=帳號或密碼輸入錯誤")
    #登入成功: 在section中記錄會員資料，導向會員頁面
    session["ID"]= result["ID"]
    return redirect("/member")
# 建立login路由 (沒有前端，會將資料送往後端)
@app.route("/logout")
def logout():
    #移除 session 中的會員資料
    del session["ID"]
    return redirect("/")

if __name__ == "__main__": #如果以主程式執行
    app.run(port=3000) #立刻啟動伺服器, 可透過 port參數 指定埠號