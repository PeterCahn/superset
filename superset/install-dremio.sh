#!/bin/bash

apt-get update

# Install DREMIO connectors
# 1) Install unixodbc - prerequisite to dremio-odbc
echo "[install-dremio.sh] Install unixodbc - prerequisite to dremio-odbc"
apt-get install -y unixodbc-dev unixodbc-bin unixodbc

# 2)Install dremio-odbc
echo "[install-dremio.sh] Install dremio-odbc"
wget https://download.dremio.com/odbc-driver/1.3.22.1055/dremio-odbc-1.3.22.1055-1.x86_64.rpm -O dremio-odbc-1.3.22.1055-1.x86_64.rpm
apt-get update
apt-get install -y alien
alien -i --script dremio-odbc-1.3.22.1055-1.x86_64.rpm

# 3) Build sqlalchemy_dremio
echo "[install-dremio.sh] Build sqlalchemy_dremio"
git clone https://github.com/ahmadimtcs/sqlalchemy_dremio.git
cd sqlalchemy_dremio
make clean

# 4) Build source and wheel package
echo "[install-dremio.sh] Build source and wheel package"
python3 setup.py sdist
python3 setup.py bdist_wheel
ls -l dist
# Run tests
<<<<<<< HEAD
#python3 -m pip install pytest
#python3 tests/conftest.py
=======
python3 -m pip install pytest
python3 tests/conftest.py
>>>>>>> 829da4c771cb5101f9f9025c46be43d7eb758ff6

# 5) Install the package to the active python3's site-packages
echo "[install-dremio.sh] Install the package to the active python3's site-packages"
python3 setup.py install
