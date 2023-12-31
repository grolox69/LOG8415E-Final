import csv
from deployer import Deployer

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

class Slave(Deployer):
    def createHosts(self):
        hosts = []
        with open('var/ec2_instances.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                if row['name'] == 'MySQL Slave':
                    hosts.append(row['public_dns_name'])
        return hosts
    
    def deployApp(self):
        if (not self.connection):
            print('No connection found. Could not start deployment')
            return
        
        # Update config files with correct Private DNS
        update_ndbconnectstring('var/ec2_instances.csv', 'mysql/cluster/slave/my.cnf')

        # Copy config files
        self.connection.run('sudo chmod 777 /etc/systemd/system && sudo chmod 777 /etc')
        self.connection.put('mysql/cluster/slave/my.cnf', remote='/etc')
        self.connection.put('mysql/cluster/slave/ndbd.service', remote='/etc/systemd/system')

        # # Setup Cluster slave
        self.connection.put('mysql/cluster/slave/slave_setup.sh', remote='/home/ubuntu')
        self.connection.run('chmod +x slave_setup.sh')
        self.connection.run('sudo bash slave_setup.sh')


if __name__ == "__main__":
    mysql_server = Slave()
    mysql_server.deployApp()