FROM python:3.9

ENV DEPLOY=1

WORKDIR /opt/app

COPY . /opt/app

COPY sources.list /etc/apt/sources.list

RUN apt-get update

RUN apt-get install -y nginx libgl1-mesa-glx vim cmake redis-server

COPY nginx.conf /etc/nginx/nginx.conf

COPY user_tools media/user_tools

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

EXPOSE 80

CMD ["sh","start.sh"]