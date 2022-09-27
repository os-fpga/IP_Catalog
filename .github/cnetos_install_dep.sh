yum group install -y "Development Tools" 
yum install -y python3 which
python3 -m pip install --upgrade pip
python3 -m pip install pipenv
curl -C - -O https://cmake.org/files/v3.15/cmake-3.15.7-Linux-x86_64.tar.gz
tar xvzf cmake-3.15.7-Linux-x86_64.tar.gz
ln -s $PWD/cmake-3.15.7-Linux-x86_64/bin/cmake /usr/bin/cmake
python3 -m pip install wheel
