from data import sync_data, init_data
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-file")
    parser.add_argument("--action")
    args = parser.parse_args()
    if args.action == "init":
        init_data(args.db_file)
    elif args.action == "sync":
        sync_data(args.db_file)
    else:
        print("Invalid action")

if __name__ == "__main__":
    main()
