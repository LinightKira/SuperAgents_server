FROM python:3.10 as builder

WORKDIR /home/app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY app_server app_server
COPY app_agent app_agent
COPY MetaGPT MetaGPT

COPY migrations migrations
#COPY config.py agents_config.json  ./
COPY config.py ./
COPY app.py   ./
#COPY fssl.key fssl.pem ./

# 合并 cd 命令到一个 RUN 指令中，确保 MetaGPT 的安装步骤正确运行
RUN cd MetaGPT && pip install --upgrade -e .

CMD ["flask","db","upgrade"]
#CMD ["python", "init_db.py"]   #初始化数据库
CMD ["python", "app.py"]


#docker run -v ${PWD}/config.py:/home/app/config.py -v ${PWD}/config2.yaml:/home/app/MetaGPT/config/config2.yaml -v ${PWD}/agents_config.json:/home/app/agents_config.json -p 5000:5000 superast