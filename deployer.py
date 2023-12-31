from abc import ABC, abstractmethod
from fabric import Connection
from fabric import ThreadingGroup

class Deployer(ABC):
    def __init__(self):
        self.hosts = [*self.createHosts()]
        self.connect_kwargs = {'key_filename': ['var/final-key.pem']}
        self.connection = self._createConnection()

    def getConnection(self):
        return self.connection
    
    def getHosts(self):
        return self.hosts

    @abstractmethod
    def createHosts(self):
        """
        Returns a list of hosts to connect 
        """
        pass
    
    def _createConnection(self):
        """
        Creates SSH connection to list of hosts 
        """
        if (not self.hosts):
            return None

        if (len(self.hosts) > 1):
            return ThreadingGroup(*self.hosts, user='ubuntu', connect_kwargs=self.connect_kwargs)

        return Connection(self.hosts[0], user='ubuntu', connect_kwargs=self.connect_kwargs)
    
    @abstractmethod
    def deployApp(self):
        """
        Deploy App to hosts
        """
        pass