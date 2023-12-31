# ref: https://www.digitalocean.com/community/tutorials/how-to-create-a-multi-node-mysql-cluster-on-ubuntu-18-04?fbclid=IwAR1m4Y8lPYDZzlpCKiSmsi4b-0roZPSidVfw1yO9dXrJ6YVcHc7Q2MKsVHY

#!/bin/bash

# Install dependencies
apt-get update
apt-get install libncurses5 libclass-methodmaker-perl -y 

# Download and install MySQL data node deamon
cd /home/ubuntu
wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster-community-data-node_7.6.6-1ubuntu18.04_amd64.deb
dpkg -i mysql-cluster-community-data-node_7.6.6-1ubuntu18.04_amd64.deb

# Creating data directory 
mkdir -p /usr/local/mysql/data

# Reload systemd manager, enable ndb_mgmd and start ndb_mgmd
systemctl daemon-reload
systemctl enable ndbd
systemctl start ndbd