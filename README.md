

## setting.py 
这个文件没有上传，可以自己新建
-m flask run
```shell script
## neo4j 配置
NEO4J_HOST = ""
NEO4J_HTTP_PORT = 7474
NEO4J_USER = ""
NEO4J_PASSORD = ""

MYSQL_HOST = ""
MYSQL_PORT = 3306
MYSQL_USER = ""
MYSQL_PASSWORD = ""
MYSQL_DB = ""
```
```shell script
#环境变量
export FLASK_APP=main.py
export FLASK_ENV=development # 或者production
conda activate "自己的虚拟环境"
gunicorn -w 4 -D -b 127.0.0.1:5000 --access-logfile ./log/log --timeout 200 main:app # 生产环境部署命令
```