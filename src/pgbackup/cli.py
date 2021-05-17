from argparse import Action, ArgumentParser


class DriverAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        driver, destination = values
        namespace.driver = driver.lower()
        namespace.destination = destination
        

def create_parser():
    parser = ArgumentParser(description="""
    Backup PostgreSQL databases locally or to aws S3.
    """)

    parser.add_argument("url", help="URL of the database to backup")
    parser.add_argument("--driver", '-d', 
    help="how and where to store backup",
    nargs=2,
    metavar=("DRIVER", "DESTINATION"),
    action=DriverAction,
    required=True)

    return parser

def main():
    import boto3
    import time
    from pgbackup import pgdump, storage

    args = create_parser().parse_args()
    dump = pgdump.dump(args.url)
    
    if args.driver == 's3':
        client = boto3.client('s3')
        timestamp = time.strftime("%Y-%m-%dT%H-%M", time.localtime())
        filename = pgdump.dump_file_name(args.url, timestamp)
        print(f"Backing up database to {args.destination} in S3 as {filename}")
        storage.s3(client, dump.stdout, args.destination, filename)
    else:
        outfile = open(args.destination, 'wb')
        print(f"Backing up database locally as {outfile.name}")
        storage.local(dump.stdout, outfile)