import csv
from deployer import Deployer

def update_hostnames_in_config(csv_file, config_file):
    # Read CSV data
    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        csv_data = [row for row in reader]

    # Separate MySQL Master and Slaves
    mysql_master = [row['private_dns_name'] for row in csv_data if 'Master' in row['name']][0]
    mysql_slaves = [row['private_dns_name'] for row in csv_data if 'Slave' in row['name']]

    # Read and parse configuration
    config_data = []
    current_section = None
    slave_index = 0
    with open(config_file) as file:
        for line in file:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                if current_section:
                    config_data.append(current_section)
                current_section = {'section': line}
            elif '=' in line:
                key, value = line.split('=', 1)
                current_section[key.strip()] = value.strip()
    if current_section:
        config_data.append(current_section)

    # Update configuration with MySQL data
    for section in config_data:
        if section['section'] in ['[ndb_mgmd]', '[mysqld]']:
            section['hostname'] = mysql_master
        elif section['section'] == '[ndbd]':
            if slave_index < len(mysql_slaves):
                section['hostname'] = mysql_slaves[slave_index]
                slave_index += 1

    # Write updated configuration
    with open(config_file, 'w') as file:
        for section in config_data:
            file.write(section['section'] + '\n')
            for key, value in section.items():
                if key != 'section':
                    file.write(f'{key}={value}\n')
            file.write('\n')

def update_ndbconnectstring(csv_file, config_file):
    # Read CSV data
    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        csv_data = [row for row in reader]

    # Extract MySQL Master's private DNS name
    mysql_master_dns = [row['private_dns_name'] for row in csv_data if 'Master' in row['name']][0]

    # Read and parse configuration
    new_config_lines = []
    with open(config_file) as file:
        for line in file:
            line = line.strip()
            if line.startswith('ndb-connectstring='):
                # Replace the existing ndb-connectstring value
                new_config_lines.append(f'ndb-connectstring={mysql_master_dns}')
            else:
                new_config_lines.append(line)

    # Write updated configuration
    with open(config_file, 'w') as file:
        for line in new_config_lines:
            file.write(line + '\n')

class Master(Deployer):
    def createHosts(self):
        hosts = []
        with open('var/ec2_instances.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                if row['name'] == 'MySQL Master':
                    hosts.append(row['public_dns_name'])
        return hosts

    def deployApp(self):
        if (not self.connection):
            print('No connection found. Could not start deployment')
            return
        
        # Update config files with correct Private DNS
        update_hostnames_in_config('var/ec2_instances.csv', 'mysql/cluster/master/config.ini')
        update_ndbconnectstring('var/ec2_instances.csv', 'mysql/cluster/master/my.cnf')

        # Copy config files
        self.connection.run('sudo mkdir -p /var/lib/mysql-cluster && sudo chmod 777 /var/lib/mysql-cluster && sudo chmod 777 /etc/systemd/system && sudo mkdir -p /etc/mysql && sudo chmod 777 /etc/mysql')
        self.connection.put('mysql/cluster/master/config.ini', remote='/var/lib/mysql-cluster')
        self.connection.put('mysql/cluster/master/ndb_mgmd.service', remote='/etc/systemd/system')
        self.connection.put('mysql/cluster/master/my.cnf', remote='/etc/mysql')

        # Deploy MySQL Cluster Management Node setup script
        self.connection.put('mysql/cluster/master/master_setup.sh', remote='/home/ubuntu/')
        self.connection.run('chmod +x master_setup.sh')
        self.connection.run('sudo bash master_setup.sh')

if __name__ == "__main__":
    mysql_server = Master()
    mysql_server.deployApp()