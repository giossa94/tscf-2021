FROM kathara/base:debian10

RUN curl -s https://deb.frrouting.org/frr/keys.asc | apt-key add -   
   
RUN echo deb https://deb.frrouting.org/frr $(lsb_release -s -c) "frr-7" | tee -a /etc/apt/sources.list.d/frr.list 

RUN echo "deb http://deb.debian.org/debian buster-backports main" | tee -a /etc/apt/sources.list

RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y frr frr-pythontools tshark python3.7 python3-pip

RUN apt install -y -t buster-backports iproute2

RUN python3 -m pip install python-daemon pyshark nest-asyncio

RUN sed -i -e 's/service/no service/' /etc/frr/vtysh.conf \
    && rm /etc/frr/frr.conf

RUN apt clean && \
    rm -rf /tmp/* /var/lib/apt/lists/* /var/tmp/*

