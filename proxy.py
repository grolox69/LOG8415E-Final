import csv
import json
from deployer import Deployer

def update_config_from_csv(csv_file_path, config_file_path):
    """ Update configuration from CSV data. """
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        master_ip = ''
        slave_ips = []
        proxy_ip = ''

        for row in reader:
            if row['name'] == 'MySQL Master':
                master_ip = row['private_dns_name']
            elif row['name'] == 'MySQL Slave':
                slave_ips.append(row['private_dns_name'])
            elif row['name'] == 'Proxy':
                proxy_ip = row['private_dns_name']

        # Read existing JSON configuration
        with open(config_file_path, 'r') as file:
            config = json.load(file)

        # Update the configuration with new data
        config['mysql_master_ip'] = master_ip
        config['mysql_slave_ips'] = slave_ips
        config['proxy_ip'] = proxy_ip

        # Write updated configuration back to JSON file
        with open(config_file_path, 'w') as file:
            json.dump(config, file, indent=4)

class Benchmark(Deployer):
    def createHosts(self):
        hosts = []
        with open('var/ec2_instances.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                if row['name'] == 'Proxy':
                    hosts.append(row['public_dns_name'])
        return hosts
    
    def deployApp(self):
        if (not self.connection):
            print('No connection found. Could not start deployment')
            return
        
        # Update Proxy Config
        update_config_from_csv('var/ec2_instances.csv', 'proxy/proxy_config.json')

        # Run Server benchmarking
        self.connection.put('proxy/proxy_app.py', remote='/home/ubuntu/')
        self.connection.put('proxy/proxy_config.json', remote='/home/ubuntu/')
        self.connection.run('sudo apt-get update')
        self.connection.run('sudo apt-get install -y python3') # Add python venv
        self.connection.run('pip3 install mysql-connector-python ping3')
        self.connection.run('python3 proxy_setup.py')

if __name__ == "__main__":
    mysql_server = Benchmark()
    mysql_server.deployApp()