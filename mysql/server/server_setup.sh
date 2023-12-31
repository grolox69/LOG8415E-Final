#!/bin/bash

# Update package information
sudo apt-get update

# Install MySQL Server
sudo apt-get install -y mysql-server

# Download and extract the Sakila sample database
cd /tmp
wget https://downloads.mysql.com/docs/sakila-db.tar.gz
tar -xzf sakila-db.tar.gz

# Execute SQL scripts to create Sakila database schema and populate data
sudo mysql -e "SOURCE /tmp/sakila-db/sakila-schema.sql;"
sudo mysql -e "SOURCE /tmp/sakila-db/sakila-data.sql;"

# Switch to the Sakila database for further use
sudo mysql -e "USE sakila;"