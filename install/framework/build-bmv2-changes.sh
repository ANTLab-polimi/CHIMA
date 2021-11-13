#!/usr/bin/bash

cd targets/simple_switch
make && sudo make install
sudo ldconfig
cd ../simple_switch_grpc
make && sudo make install
sudo ldconfig
ls -la /usr/local/bin/ | grep simple_switch
