import csv
from deployer import Deployer

class Benchmark(Deployer):
    def createHosts(self):
        hosts = []
        with open('var/ec2_instances.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                if row['name'] == 'MySQL Server' or row['name'] == 'MySQL Master':
                    hosts.append(row['public_dns_name'])
        return hosts
    
    def deployApp(self):
        if (not self.connection):
            print('No connection found. Could not start deployment')
            return
        
        # Run Server benchmarking
        self.connection[0].put('mysql/benchmark/server_benchmark.sh', remote='/home/ubuntu/')
        self.connection[0].run('chmod +x server_benchmark.sh')
        self.connection[0].run('./server_benchmark.sh')

        # Run Cluster benchmarking
        self.connection[1].put('mysql/benchmark/cluster_benchmark.sh', remote='/home/ubuntu/')
        self.connection[1].run('chmod +x cluster_benchmark.sh')
        self.connection[1].run('sudo ./cluster_benchmark.sh')


if __name__ == "__main__":
    mysql_server = Benchmark()
    mysql_server.deployApp()