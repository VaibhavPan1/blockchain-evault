import ipfshttpclient
import requests

class IPFSHandler:
    def __init__(self, ipfs_url = "/ip4/127.0.0.1/tcp/5001"): #multiformat url
        self.client = ipfshttpclient.connect(ipfs_url)
        self.ipfs_url = ipfs_url
        print("connected to ipfs")
    
    def upload_file(self, file_path):
        result = self.client.add(file_path)
        
        # print("result = ", result)

        #for directory uploads
        if isinstance(result, list):
            return result[-1]['Hash']
        
        #for file uploads
        return result['Hash'] #CID
    
    def get_file(self, cid):
        # response = requests.get(f'{self.ipfs_url}')
        return self.client.cat(cid)
        # return self.client.get(cid)
        # print(f"saved to {output_path}")

