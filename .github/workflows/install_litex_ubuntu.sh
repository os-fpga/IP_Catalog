# Install required dependencies for Ubuntu systems
sudo apt-get update -qq
sudo apt install -y \
  build-essential \
  python3 \
  ninja-build \
  libevent-dev \
  libjson-c-dev \
  flex \
  tree \
  bison \
  libfl-dev \
  libfl2 \
  zlibc \
  zlib1g-dev

# Install required Python3 packages.
pip3 install \
  setuptools \
  requests \
  pexpect \
  meson

