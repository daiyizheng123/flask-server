
```shell script
#环境变量
export FLASK_APP=main.py
export FLASK_ENV=development # 或者production
conda activate "自己的虚拟环境"
gunicorn -w 4 -b 127.0.0.1:5000 -D --access-logfile ./logs/log main:app # 生产环境部署命令
```