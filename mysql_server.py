import csv
from deployer import Deployer 

class Server(Deployer):
    def createHosts(self):
        with open('var/ec2_instances.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                if row['name'] == 'MySQL Server':
                    return [row['public_dns_name']]
    
    def deployApp(self):
        if (not self.connection):
            print('No connection found. Could not start deployment')
            return
        
        # Install MySQL Server
        self.connection.put('mysql/server/server_setup.sh', remote='/home/ubuntu/')
        self.connection.run('chmod +x server_setup.sh')
        self.connection.run('./server_setup.sh')

if __name__ == "__main__":
    mysql_server = Server()
    mysql_server.deployApp()