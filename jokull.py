import argparse
import json
import os
import time

import boto.glacier.layer2

aws_params = {
    'aws_access_key_id': os.environ['AWS_ACCESS'],
    'aws_secret_access_key': os.environ['AWS_SECRET'],
}

class IndexedVault(object):
    def __init__(self, jokull, vault):
        self.jokull = jokull
        self.vault = vault

    def request_inventory(self):
        if any(j.action == 'InventoryRetrieval' for j in self.vault.list_jobs(completed=False)):
            raise RuntimeError("There is already a pending job for inventory retrieval")
        self.vault.retrieve_inventory()

    def upload_archive(self, path, desc=None):
        if not self.jokull.index:
            raise RuntimeError("Index file is required for uploads")
        if not desc:
            desc = "archive of '%s' in '%s'" % (path, self.vault.name)
        record = {
            'desc': desc,
            'path': path,
            'size': os.stat(path).st_size,
            'start': int(time.time()),
        }
        try:
            record['archive_id'] = self.vault.upload_archive(path, desc)
            record['end'] = int(time.time())
        except Exception:
            print "Failed upload! Incomplete record:", record
            raise
        print "Uploaded! Completed record:", record
        self.jokull.append_record(self.vault.name, record)
 
class Jokull(object):
    def __init__(self, indexpath):
        self.indexpath = indexpath
        self.index = None
        if self.indexpath:
            with open(indexpath) as fp:
                self.index = json.load(fp)
                assert isinstance(self.index, dict)
        api = boto.glacier.layer2.Layer2(**aws_params)
        self.vaults = api.list_vaults()

    def get_vault(self, vaultname):
        try:
            vault = [v for v in self.vaults if v.name == vaultname][0]
        except IndexError:
            raise KeyError("Vault '%s' does not exist" % vaultname)
        return IndexedVault(self, vault)

    def append_record(self, vaultname, record):
        if vaultname not in self.index:
            self.index[vaultname] = []
        vault_index = self.index[vaultname]
        try:
            vault_index.append(record)
            with open(self.indexpath, 'w') as fp:
                json.dump(self.index, fp, indent=4)
        except Exception:
            print "Failed index! Completed record:", record


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('vault')
    parser.add_argument('--index', default='index.json')
    parser.add_argument('--desc')
    args = parser.parse_args()

    jokull = Jokull(args.index)
    vault = jokull.get_vault(args.vault)
    vault.upload_archive(args.path, args.desc)
