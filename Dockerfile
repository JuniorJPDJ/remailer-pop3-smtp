FROM python:3-alpine

WORKDIR /opt/remailer-pop3-smtp

COPY crontab.Docker /etc/crontabs/root
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# You need to provide config.yaml on a buildtime or mount it as a volume to container later

CMD [ "crond", "-f", "-d", "8" ]
