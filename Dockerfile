FROM debian:latest

ARG DISCORD_TOKEN
ARG DEEPL_TOKEN

ENV DEBIAN_FRONTEND=noninteractive
ENV USER BotMaster
ENV WORK /home/${USER}
ENV SHELL /bin/bash 

ENV DISCORD_TOKEN $DISCORD_TOKEN
ENV DEEPL_TOKEN $DEEPL_TOKEN

###### Deps ######
RUN rm -rf /var/lib/apt/lists/* ; apt-get clean;apt-get update --fix-missing;apt-get -y --yes upgrade
RUN apt-get -y -qq install --yes sudo bash nano netcat wget iproute2 curl git python3 python3-pip
RUN python3 -m pip install --upgrade pip
##################

##### Config ######

RUN useradd -m -s /bin/bash ${USER} ;\
	echo "${USER}:${USER}" | chpasswd ;\
	echo "cd /home/${USER}/Discord-CTFD-Parser;" >> /root/.bashrc ;\
	chown -R ${USER} /home/${USER}

RUN \
	mkdir ${WORK} ;\
	cd "/home/${USER}" ;\
	git clone https://github.com/Vozec/Discord-CTFD-Parser.git ;\
	cd Discord-CTFD-Parser ;\
	python3 -m pip install -r requirements.txt

##################

WORKDIR ${WORK}
CMD ["python3","./Discord-CTFD-Parser/app.py"]
