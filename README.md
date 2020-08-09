

## setting.py 
这个文件没有上传，可以自己新建
```shell script
## neo4j 配置
NEO4J_HOST = ""
NEO4J_HTTP_PORT = 7474
NEO4J_USER = ""
NEO4J_PASSORD = ""
```
```shell script
#环境变量
export FLASK_APP=main.py
export FLASK_ENV=development # 或者production
conda activate "自己的虚拟环境"
gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile ./log/log main:app --log-level=debug --timeout 120 # 生产环境部署命令
```