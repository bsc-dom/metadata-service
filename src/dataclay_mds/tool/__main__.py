import sys
import argparse
import logging

from dataclay_mds.tool import functions

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def new_account(args):
    return functions.new_account(args.username, args.password)

def new_session(args):
    return functions.new_session(args.username, args.password)

def get_backends(args):
    return functions.get_backends(args.username, args.password)


if __name__ == "__main__":

    # Create the top-level parser
    parser = argparse.ArgumentParser(description='Dataclay tool')
    # TODO: Remove "dest" for new python versions
    subparsers = parser.add_subparsers(dest='function', required=True)

    # Create the parser for the "new_account" command
    parser_new_account = subparsers.add_parser('new_account')
    parser_new_account.add_argument('username', type=str)
    parser_new_account.add_argument('password', type=str)
    parser_new_account.set_defaults(func=new_account)

    # Create the parser for the "new_session" command
    parser_new_session = subparsers.add_parser('new_session')
    parser_new_session.add_argument('username', type=str)
    parser_new_session.add_argument('password', type=str)
    parser_new_session.set_defaults(func=new_session)

    # Create the parser for the "get_backends" command
    parser_new_account = subparsers.add_parser('get_backends')
    parser_new_account.add_argument('username', type=str)
    parser_new_account.add_argument('password', type=str)
    parser_new_account.set_defaults(func=get_backends)

    # TODO: Create the parser for the other commands

    args = parser.parse_args()
    args.func(args)