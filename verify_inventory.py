import time

import jokull
import util

def verify_inventory(job_output, index):
    vaultname = job_output['VaultARN'].split('/')[-1]
    inventory_time = util.parse_8601(job_output['InventoryDate'])
    local_hash = {a['archive_id']: a for a in index[vaultname]}
    remote_hash = {a['ArchiveId']: a for a in job_output['ArchiveList']}
    for rec in local_hash.itervalues():
        if rec['end'] + 25200 > inventory_time:  # give it 7 hours or so?
            print "Skipping archive %s (completed %.1f hours ago)" % (rec['archive_id'], util.hours_ago(rec['end']))
            continue
        remote_rec = remote_hash.get(rec['archive_id'])
        assert remote_rec, "Index record %r is missing from inventory" % rec
        assert rec['size'] == remote_rec['Size'], "Index record %r differs in size from inventory record %r" % (rec, remote_rec)
        assert -300 < rec['end'] - util.parse_8601(remote_rec['CreationDate']) < 300, "Index record %r differs in timestamp from inventory record %r" % (rec, remote_rec)
    for remote_id in remote_hash:
        assert remote_id in local_hash, "Inventory record %r is missing from index!" % remote_hash[remote_id]
    print "OK"

if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument('--inventory')
    parser.add_argument('--vault')
    parser.add_argument('--index', default='index.json')
    args = parser.parse_args()
    with open(args.index) as fp:
        index = json.load(fp)
    if args.inventory:
        with open(args.inventory) as fp:
            job_output = json.load(fp)
    else:
        if not args.vault:
            raise RuntimeError("At least one of --inventory or --vault must be provided")
        job_output = jokull.Jokull(indexpath=None).get_vault(args.vault).get_last_inventory_job().get_output()
    verify_inventory(job_output, index)
