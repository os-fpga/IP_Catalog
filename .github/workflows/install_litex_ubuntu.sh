# Install required dependencies for Ubuntu systems
sudo apt-get update -qq
sudo apt install -y \
  build-essential \
#  python3 \
  ninja-build \
  libevent-dev \
  libjson-c-dev \
  flex \
  bison \
  libfl-dev \
  libfl2 \
#  verilator \
  zlibc \
  zlib1g-dev

# Install required Python3 packages.
pip3 install \
  setuptools \
  requests \
  pexpect \
  meson


# Download/Install LiteX.
wget https://raw.githubusercontent.com/enjoy-digital/litex/master/litex_setup.py
chmod +x litex_setup.py
./litex_setup.py --init --config minimal
sudo ./litex_setup.py --install --config minimal

# Download/Install RISC-V GCC toolchain.
#./litex_setup.py --gcc=riscv
#sudo mkdir /usr/local/riscv
#sudo cp -r riscv64-*/* /usr/local/riscv
