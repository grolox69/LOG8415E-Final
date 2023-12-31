#!/bin/bash

# Install sysbench for benchmarking
sudo apt-get install -y sysbench

sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --mysql-user=root --mysql-password=root prepare

# Run sysbench OLTP read-write test with specific configurations and redirect output to standaloneResult.txt
sysbench oltp_read_write --table-size=100000 --threads=6 --time=60 --max-requests=0 --mysql-db=sakila --mysql-user=root --mysql-password=root run > clusterResults.txt

# Cleanup the database after sysbench OLTP read-write test
sysbench oltp_read_write --mysql-db=sakila --mysql-user=root --mysql-password=root cleanup