sudo apt-get update
sudo apt install -y cmake build-essential
sudo apt-get install iverilog
#sudo apt install -y python3 python3-pip
#python3 -m pip install --upgrade pip
#python3 -m pip install pipenv
python3 -m pip install cocotb==1.7.1
python3 -m pip install cocotb-bus=0.1.1
python3 -m pip install cocotb-test==0.2.1
python3 -m pip install cocotbext-axi==0.1.18
python3 -m pip install myhdl
sudo ln -sf /usr/lib/x86_64-linux-gnu/libffi.so.7.1.0 /usr/lib/x86_64-linux-gnu/libffi.so.6

