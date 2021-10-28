FROM kathara/frr

RUN apt -y update; \
    apt -y upgrade; \
    DEBIAN_FRONTEND=noninteractive apt install -y apt-utils \
    tshark
