#dependencies
sudo apt install -y bison build-essential cmake flex git libedit-dev \
    libllvm7 llvm-7-dev libclang-7-dev clang-7 python zlib1g-dev libelf-dev libfl-dev

#compile
cd
git clone https://github.com/iovisor/bcc.git
cd bcc
git checkout e12ec044f5d9f78c17075304299e3942416dd3de
mkdir build; cd build
cmake -DPYTHON_CMD=python3 -DCMAKE_PREFIX_PATH=/usr/lib/llvm-7 ..
make
sudo make install
# build python3 binding
cmake -DPYTHON_CMD=python3 .. 
pushd src/python/
make
sudo make install
popd
