# Install required dependencies for CentOS systems
yum update -y
yum install -y "Development Tools"
yum install -y python3
yum install -y ninja-build
yum install -y glibc-devel.i68
yum install -y libevent-devel
yum install -y json-c-devel
yum install -y flex
yum install -y bison
yum install -y verilator

# Install required Python3 packages.
pip3 install \
  setuptools \
  requests \
  pexpect \
  meson

