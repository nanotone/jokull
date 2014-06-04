import jokull

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('vault')
    args = parser.parse_args()
    jokull.Jokull(None).get_vault(args.vault).request_inventory()
