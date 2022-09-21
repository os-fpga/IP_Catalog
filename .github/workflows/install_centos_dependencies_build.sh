# Install required dependencies for CentOS systems
curl -C - -O https://cmake.org/files/v3.15/cmake-3.15.7-Linux-x86_64.tar.gz
tar xzf cmake-3.15.7-Linux-x86_64.tar.gz
ln -s $PWD/cmake-3.15.7-Linux-x86_64/bin/cmake /usr/bin/cmake
