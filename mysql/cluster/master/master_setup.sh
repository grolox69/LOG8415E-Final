# ref: https://www.digitalocean.com/community/tutorials/how-to-create-a-multi-node-mysql-cluster-on-ubuntu-18-04?fbclid=IwAR1m4Y8lPYDZzlpCKiSmsi4b-0roZPSidVfw1yO9dXrJ6YVcHc7Q2MKsVHY

#!/bin/bash

# Install dependencies
sudo apt-get update
sudo apt-get install libncurses5 libaio1 libmecab2 sysbench -y

# Download and install the MySQL Cluster Manager, ndb_mgmd
cd /home/ubuntu
wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb
dpkg -i mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb

# Reload systemd manager, enable ndb_mgmd and start ndb_mgmd
systemctl daemon-reload
systemctl enable ndb_mgmd
systemctl start ndb_mgmd

# Download MySQL Server
wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster_7.6.6-1ubuntu18.04_amd64.deb-bundle.tar
mkdir install
tar -xvf mysql-cluster_7.6.6-1ubuntu18.04_amd64.deb-bundle.tar -C install/
cd install

# Install MySQL Server
dpkg -i mysql-common_7.6.6-1ubuntu18.04_amd64.deb
dpkg -i mysql-cluster-community-client_7.6.6-1ubuntu18.04_amd64.deb
dpkg -i mysql-client_7.6.6-1ubuntu18.04_amd64.deb

# Configure installation to avoid using MySQL prompt
debconf-set-selections <<< 'mysql-cluster-community-server_7.6.6 mysql-cluster-community-server/root-pass password root'
debconf-set-selections <<< 'mysql-cluster-community-server_7.6.6 mysql-cluster-community-server/re-root-pass password root'

# Install the rest of the packages
dpkg -i mysql-cluster-community-server_7.6.6-1ubuntu18.04_amd64.deb
dpkg -i mysql-server_7.6.6-1ubuntu18.04_amd64.deb

# Restart MySQL Server
systemctl restart mysql
systemctl enable mysql

# Download Sakila database
cd /home/ubuntu
wget https://downloads.mysql.com/docs/sakila-db.tar.gz -O /home/ubuntu/sakila-db.tar.gz
tar -xvf /home/ubuntu/sakila-db.tar.gz -C /home/ubuntu/

# Upload Sakila database to MySQL
mysql -u root -proot -e "SOURCE /home/ubuntu/sakila-db/sakila-schema.sql;"
mysql -u root -proot -e "SOURCE /home/ubuntu/sakila-db/sakila-data.sql;"
