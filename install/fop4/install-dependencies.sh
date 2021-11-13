#!/bin/bash

#Prerequisites
#Adapted from https://github.com/ANTLab-polimi/FOP4/blob/master/util/install-p4-dependencies.sh

framework_root=$(pwd)

#Install everything in the home directory
cd

#Install basic packages
sudo apt update
sudo apt install python3-pip -y

#Install dependencies with the script from https://github.com/jafingerhut/p4-guide/blob/master/bin/README-install-troubleshooting.md
git clone https://github.com/jafingerhut/p4-guide
git checkout 771ec595b3a911d77ea0fd8d6046df8c3a19c702
cp $framework_root/install/fop4/install-p4dev-v4-framework.sh ./p4-guide/bin/
chmod +x ./p4-guide/bin/install-p4dev-v4-framework.sh
./p4-guide/bin/install-p4dev-v4-framework.sh |& tee dependencies_log.txt

#Add paths to environment
cat p4setup.bash >> .profile
echo "export CHIMA_ROOT=$framework_root" >> .profile

#Uninstall mininet pip package installed by the script, it will be substituded by the one of Containernet
#Otherwise 'sudo python3 setup.py install' doesn't work correctly
sudo pip3 uninstall -y mininet
