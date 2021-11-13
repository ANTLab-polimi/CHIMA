#!/bin/bash

#Prerequisites
#Adapted from https://github.com/ANTLab-polimi/FOP4/blob/master/util/install-p4-dependencies.sh

framework_root=$(pwd)

#Install everything in the home directory
cd

#Clone and install FOP4
git clone https://github.com/ANTLab-polimi/FOP4.git
cd FOP4
git checkout 6edf95398f8fd93b0d8f52ebf666a8dc6c0b27ab
cd ansible

#Run ansible
sudo apt-get install -y ansible aptitude
sudo ansible-playbook -i "localhost," -c local install.yml
cd ..

#Apply patch to be able to use containers in priviledged mode
#This is needed for docker in docker (dind)
git apply $framework_root/install/patches/priviledged_containers.patch

#Install FOP4 as a python3 package
sudo python3 setup.py install

sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker

#For some reason this script stays hanging
exit