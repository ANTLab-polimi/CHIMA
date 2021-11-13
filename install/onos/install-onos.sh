#!/usr/bin/bash

ONOS_VERSION="5bdbe43567be4f46b855c6efa077d7e5d57a819d"

echo "Installing dependencies..."
sudo apt install -y python2 wget openjdk-11-jdk curl zip unzip golang

echo "Installing bazelisk.."
go get github.com/bazelbuild/bazelisk
BAZEL="$HOME/go/bin/bazelisk"
sudo ln -s $BAZEL /usr/bin/bazel

echo "Creating python symlink if it doesn't exist"
sudo ln -s /usr/bin/python2 /usr/bin/python
curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output /tmp/get-pip.py
sudo python2 /tmp/get-pip.py
pip2 install requests

cd
echo "Installing onos..."
git clone https://github.com/opennetworkinglab/onos.git
cd onos
git checkout $ONOS_VERSION

cat << EOF >> ~/.profile
export ONOS_ROOT="`pwd`"
source \$ONOS_ROOT/tools/dev/bash_profile
EOF

source $HOME/.profile

#Apply patches
git apply $CHIMA_ROOT/install/patches/onos-targetlist-inbandtelemetry.patch
git apply $CHIMA_ROOT/install/patches/pipeconfwatchdog.patch
git apply $CHIMA_ROOT/install/patches/public-flowrules.patch

onos-publish -l

rm -r ./pipelines/basic/src/main/*
cp -r $CHIMA_ROOT/pipeline/* ./pipelines/basic/src/main/
make -C pipelines/basic/src/main/resources

bazel build onos