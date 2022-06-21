import requests

import logging

_LOGGER = logging.getLogger(__name__)

class HomeWizardREST():
    def __init__(self, host, password) -> None:
      self._base_url = f'http://{host}/{password}'

    def fetch(self, url):
      _LOGGER.fatal(f'Fetching: {url}')
      req = requests.get(f'{self._base_url}{url}', timeout=5)

      if req.status_code != 200:
        return None
      
      return req.json()

    def get_switches(self):
      sensors = self.fetch("/get-sensors")
      if sensors == None:
        return []
      _LOGGER.fatal(sensors)
      return sensors['response']["switches"]
    
    def get_switch(self, id):
      switches = self.get_switches()
      for switch in switches:
        if switch['id'] == id:
          return switch
    
    def set_dimmer(self, id, brightness):
      res = self.fetch(f'/sw/dim/{id}/{brightness}')
      _LOGGER.fatal(res)
      return res

    def turn_switch(self, id, state):
      res = self.fetch(f'/sw/{id}/{state}')
      _LOGGER.fatal(res)
      return res