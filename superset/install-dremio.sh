#!/bin/bash

# Install DREMIO connectors
# 1) Install unixodbc - prerequisite to dremio-odbc
apt-get install -y unixodbc-dev unixodbc-bin unixodbc

# 2)Install dremio-odbc
wget https://download.dremio.com/odbc-driver/1.3.22.1055/dremio-odbc-1.3.22.1055-1.x86_64.rpm -O dremio-odbc-1.3.22.1055-1.x86_64.rpm
apt-get install -y alien
alien -i dremio-odbc-1.3.22.1055-1.x86_64.rpm

# 3) Build sqlalchemy_dremio
git clone https://github.com/ahmadimtcs/sqlalchemy_dremio.git
cd sqlalchemy_dremio
make clean

# 4) Build source and wheel package
python3 setup.py sdist
python3 setup.py bdist_wheel
ls -l dist
# Run tests
python3 -m pip install pytest
python3 sqlalchemy_dremio/tests/conftest.py

# 5) Install the package to the active python3's site-packages
python3 setup.py install

# 6) Replace file with changes
cp -f /etc/superset/sql_lab.py /usr/local/lib/python3.6/site-packages/superset/sql_lab.py
cp -f /etc/superset/dataframe.py /usr/local/lib/python3.6/site-packages/superset/dataframe.py


