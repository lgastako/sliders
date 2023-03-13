import fire
import requests

from swagger_parser import SwaggerParser

class CLI:
    def from_url(self, url):
        resp = requests.get(url)
        # write the results to a file to read with SwaggerParser
        with open("swagger.json", "w") as f:
            f.write(resp.text)
        parser = SwaggerParser("swagger.json")
        import ipdb; ipdb.set_trace()
        
if __name__ == '__main__':
    fire.Fire(CLI)