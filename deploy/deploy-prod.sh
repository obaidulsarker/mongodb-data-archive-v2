#!/bin/bash

HOME=/data/app/mongodb-archive

LOGFILE=$HOME/deploy.log

DOCKER_REG_HOST_IP=xxx.xxx.xxx.xx
DOCKER_REG=xxx.xxx.xxx.xx
HARBOR_USER="user1"

PROJECT_NAME=mongo-db-archive
ARCHIVE_REPO_NAME=mongo-db-archive
NOTFICATION_REPO_NAME=mongo-db-archive-notification
APP_VERSION=latest

echo "$(date) : [$PROJECT_NAME] deployment is started." >> $LOGFILE;
echo "$(date) : [$PROJECT_NAME] ***********************" >> $LOGFILE;
# Login to Harbor registry

echo "$(date) : [$PROJECT_NAME] docker login .." >> $LOGFILE;
cat docker-reg-password.txt | docker login $DOCKER_REG --username "$HARBOR_USER" --password-stdin >> $LOGFILE;

sudo docker ps --filter status=exited -q | xargs docker rm

echo "$(date) : [$ARCHIVE_APP_REPO] docker image pull .." >> $LOGFILE;
docker pull $DOCKER_REG_HOST_IP/$PROJECT_NAME/$ARCHIVE_REPO_NAME:$APP_VERSION

echo "$(date) : [$ARCHIVE_APP_REPO] docker run .." >> $LOGFILE;
docker run -v $HOME/logs:/app/logs -v $HOME/cred:/app/cred -v $HOME/config:/app/config -d $DOCKER_REG_HOST_IP/$PROJECT_NAME/$ARCHIVE_REPO_NAME:$APP_VERSION

echo "$(date) : [$NOTFICATION_REPO_NAME] docker image pull .." >> $LOGFILE;
docker pull $DOCKER_REG_HOST_IP/$PROJECT_NAME/$NOTFICATION_REPO_NAME:$APP_VERSION

echo "$(date) : [$NOTFICATION_REPO_NAME] docker run .." >> $LOGFILE;
docker run -v $HOME/logs:/app/logs -v $HOME/cred:/app/cred -v $HOME/config:/app/config -d $DOCKER_REG_HOST_IP/$PROJECT_NAME/$NOTFICATION_REPO_NAME:$APP_VERSION

echo "$(date) : [$PROJECT_NAME] deployment is completed" >> $LOGFILE;
