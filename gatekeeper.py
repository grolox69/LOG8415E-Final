import csv
import json
from deployer import Deployer

class Gatekeeper(Deployer):
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

        # Run Server benchmarking
        self.connection.put('gatekeeper/gatekeeper_app.py', remote='/home/ubuntu/')
        self.connection.put('gatekeeper/trusted_hosts.py', remote='/home/ubuntu/')
        self.connection.run('sudo apt-get update')
        self.connection.run('sudo apt-get install -y python3')
        self.connection.run('sudo apt install -y flask')
        self.connection.run('python3 gatekeeper_app.py')
        self.connection.run('python3 trusted_hosts.py')

if __name__ == "__main__":
    mysql_server = Gatekeeper()
    mysql_server.deployApp()