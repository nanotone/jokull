import argparse
import json
import os
import time

import boto.glacier.layer2

aws_params = {
    'aws_access_key_id': 'AKIAJM2CMARNBGAXPQEQ',
    'aws_secret_access_key': '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',
}

class IndexedVault(object):
    def __init__(self, jokull, vault):
        self.jokull = jokull
        self.vault = vault

    def upload_archive(self, path, desc):
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
    parser.add_argument('--desc', default='')
    args = parser.parse_args()
    desc = args.desc or "archive of '%s' in '%s'" % (args.path, args.vault)

    jokull = Jokull(args.index)
    vault = jokull.get_vault(args.vault)
    vault.upload_archive(args.path, desc)
