sudo ip link add veth_1 type veth peer name veth_2
sudo ip link set dev veth_1 address 00:00:00:00:00:20
sudo ip link set dev veth_2 address 00:00:00:00:00:20
sudo ip link set dev veth_1 up
sudo ip link set dev veth_2 up
sudo ip addr add 10.0.0.200/24 dev veth_1
ethtool --offload veth_1 rx off  tx off
ethtool -K veth_1 gso off
