#!/bin/bash

# Install sysbench for benchmarking
sudo apt-get install -y sysbench

# Prepare the database for sysbench OLTP read-write test
sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root prepare

# Run sysbench OLTP read-write test with specific configurations and redirect output to results.txt
sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root --num-threads=6 --max-time=60 --max-requests=0 run > results.txt

# Cleanup the database after sysbench OLTP read-write test
sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root cleanup