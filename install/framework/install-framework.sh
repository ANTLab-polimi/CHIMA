#!/usr/bin/bash

#Apply patch to bmv2 and rebuild
source $HOME/.profile
cd $P4_INSTALL/behavioral-model
git apply $CHIMA_ROOT/install/patches/bmv2-clone-clock.patch

cp $CHIMA_ROOT/install/framework/build-bmv2-changes.sh .
./build-bmv2-changes.sh

#Install needed packages
sudo apt install -y maven docker-compose expect
sudo pip3 install pytest pyroute2 flask pyvis prometheus_client

#Build stub
cd $CHIMA_ROOT/chima-stub
make build

#Build hosts Docker In Docker image
cd $CHIMA_ROOT/dind
./loadclient.sh
./build_container.sh

#Install BCC
cd $CHIMA_ROOT/install/framework
./bcc-compilesource.sh

#Install Prometheus
sudo groupadd --system prometheus
sudo useradd -s /sbin/nologin --system -g prometheus prometheus
sudo mkdir /var/lib/prometheus
for i in rules rules.d files_sd; do sudo mkdir -p /etc/prometheus/${i}; done
mkdir -p /tmp/prometheus && cd /tmp/prometheus
curl -s https://api.github.com/repos/prometheus/prometheus/releases/latest | grep browser_download_url | grep linux-amd64 | cut -d '"' -f 4 | wget -i -
tar xvf prometheus*.tar.gz
cd prometheus*/
sudo mv prometheus promtool /usr/local/bin/
sudo mv consoles/ console_libraries/ /etc/prometheus/
cd $CHIMA_ROOT/install/framework
sudo cp prometheus.yml /etc/prometheus/prometheus.yml
sudo cp prometheus.service /etc/systemd/system/prometheus.service

for i in rules rules.d files_sd; do sudo chown -R prometheus:prometheus /etc/prometheus/${i}; done
for i in rules rules.d files_sd; do sudo chmod -R 775 /etc/prometheus/${i}; done
sudo chown -R prometheus:prometheus /var/lib/prometheus/

sudo systemctl daemon-reload
sudo systemctl start prometheus
sudo systemctl enable prometheus