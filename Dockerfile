FROM ubuntu:noble

RUN apt-get update

RUN apt-get install -y python3 python3-dev pipx make gcc g++ software-properties-common libffi-dev libcairo2-dev libpango-1.0-0

RUN apt-add-repository ppa:ubuntugis/ubuntugis-unstable && apt-get install -y gdal-bin libgdal-dev

RUN pipx ensurepath

RUN pipx install poetry==1.4.2
