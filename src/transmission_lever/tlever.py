#!/usr/bin/env python

import logging
import argparse
from importlib.metadata import requires

from transmission_lever.core.client import get_client
from transmission_lever.core.config import get_config
from transmission_lever.core.label import mk_label, rm_label
from transmission_lever.extra.category import mk_category, rm_category, enforce_categories
from transmission_lever.extra.tag import mk_tag, rm_tag
from transmission_lever.extra.tier import set_tiers, unset_tiers, activate_tiers
from transmission_lever.extra.tui import curses_single
from transmission_lever.extra.clog import set_clog, unset_clog


def main():

    #
    # Create main parser
    #
    description = 'Simplifies common chores on torrents by wrapping the RPC'
    epilog      = 'Not all RPC methods are properly documented on upstream'

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog)

    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='Show verbose output')

    subparsers = parser.add_subparsers(help='Modifier on a torrent',
                                       dest='command',
                                       required=True)

    ##
    ## Create sub-parser for 'category' command
    ##
    description = 'Simulates categories with labels and moves the torrent data'

    category_parser = subparsers.add_parser('category',
                                            description=description,
                                            help='Manages categories of torrents')

    category_subparsers = category_parser.add_subparsers(dest='category_command')

    ###
    ### Create sub-sub-parser for 'category add' command
    ###
    category_add_parser = category_subparsers.add_parser('add',
                                   help='Add a category to a torrent')

    category_add_parser.add_argument('name',
                                     type=str,
                                     help='Name of the category (without prefix)')

    category_add_parser.add_argument('hash',
                                     type=str,
                                     help='Hash of the target torrent',)

    ###
    ### Create sub-sub-parser for 'category remove' command
    ###
    category_remove_parser = category_subparsers.add_parser('remove',
                                                            help='Remove a category from a torrent')

    category_remove_parser.add_argument('name',
                                        type=str,
                                        help='Name of the category (without prefix)',)

    category_remove_parser.add_argument('hash',
                                        type=str,
                                        help='Hash of the target torrent',)

    ###
    ### Create sub-sub-parser for 'category enforce' command
    ###
    category_subparsers.add_parser('enforce',
                                   help='Enforce a category on a torrent')

    ##
    ## Create sub-parser for 'label' command
    ##
    description = 'Manages labels without prefixes'

    label_parser = subparsers.add_parser('label',
                                         description=description,
                                         help='Manages labels of torrents')

    label_subparsers = label_parser.add_subparsers(dest='category_command')

    ###
    ### Create sub-sub-parser for 'label add' command
    ###
    label_add_parser = label_subparsers.add_parser('add',
                                                   help='Add a label to a torrent')

    label_add_parser.add_argument('name',
                                  type=str,
                                  help='Name of the label',)

    label_add_parser.add_argument('hash',
                                  type=str,
                                  help='Hash of the target torrent')

    ###
    ### Create sub-sub-parser for 'label remove' command
    ###
    label_remove_parser = label_subparsers.add_parser('remove',
                                                   help='Remove a label to a torrent')

    label_remove_parser.add_argument('name',
                                  type=str,
                                  help='Name of the label',)

    label_remove_parser.add_argument('hash',
                                  type=str,
                                  help='Hash of the target torrent')

    ##
    ## Create sub-parser for 'tag' command
    ##
    description = 'Simulates tags with prefixed labels'

    tag_parser = subparsers.add_parser('tag',
                                       description=description,
                                       help='Manages tags of torrents')

    tag_subparsers = tag_parser.add_subparsers(dest='tag_command')

    ###
    ### Create sub-sub-parser for 'tag add' command
    ###
    tag_add_parser = tag_subparsers.add_parser('add',
                                                   help='Add a tag to a torrent')

    tag_add_parser.add_argument('name',
                                type=str,
                                help='Name of the tag',)

    tag_add_parser.add_argument('hash',
                                type=str,
                                help='Hash of the target torrent',)

    ###
    ### Create sub-sub-parser for 'tag remove' command
    ###
    tag_remove_parser = tag_subparsers.add_parser('remove',
                                                   help='Remove a tag to a torrent')

    tag_remove_parser.add_argument('name',
                                type=str,
                                help='Name of the tag',)

    tag_remove_parser.add_argument('hash',
                                type=str,
                                help='Hash of the target torrent',)

    ##
    ## Create sub-parser for 'tier' command
    ##
    description = 'Enforces upload speed throttle based on ratio using prefixed labels'

    tier_parser = subparsers.add_parser('tier',
                                        description=description,
                                        help='Manages upload limit based on ratio')

    tier_subparsers = tier_parser.add_subparsers(dest='tier_command')

    ###
    ### Create sub-sub-parser for 'tier set' command
    ###
    tier_subparsers.add_parser('set',
                               help='Add tier tags and apply upload limits')

    ###
    ### Create sub-sub-parser for 'tier unset' command
    ###
    tier_subparsers.add_parser('unset',
                              help='Remove tier tags and reset upload limits')

    ###
    ### Create sub-sub-parser for 'tier activate'
    ###
    tier_subparsers.add_parser('activate',
                               help='Start tier tagged torrents')

    ###
    ### Create sub-sub-parser for 'tier enforce'
    ###
    tier_subparsers.add_parser('enforce',
                               help='Alias for set + activate')

    ##
    ## Create sub-parser for 'tui' command
    ##
    tui_parser = subparsers.add_parser('tui',
                                       help='Starts ncurses interface')

    tui_subparsers = tui_parser.add_subparsers(dest='tui_command')

    ###
    ### Create sub-sub-parser 'tui show' command
    ###
    tui_show_parser = tui_subparsers.add_parser('show',
                                                help='Show live updates of a torrent')
    tui_show_parser.add_argument('hash',
                                 help='Hash of the target torrent',)

    ##
    ## Create sub-parser 'clog' command
    ##
    clog_parser = subparsers.add_parser('clog',
                                        help='Manages upload limit above tier bounds')

    clog_parser.add_argument('action',
                             type=str,
                             choices=['set', 'unset'],
                             help='Action to perform')

    # parse arguments
    args = parser.parse_args()

    # debug on
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
        print(vars(args))
    else:
        logging.basicConfig(level=logging.WARNING)

    # parse config file
    cfg = get_config()
    client = get_client(cfg)

    if args.command == 'category':
        if args.category_command == 'add':
            mk_category(cfg, args.hash, args.name)

        elif args.category_command == 'remove':
            rm_category(cfg, args.hash, args.name)

        elif args.category_command == 'enforce':
            enforce_categories(cfg)

    elif args.command == 'label':
        if args.label_command == 'add':
            mk_label(client, args.hash, args.name)

        elif args.label_command == 'remove':
            rm_label(client, args.hash, args.name)

    elif args.command == 'tag':
        if args.tag_command == 'add':
            mk_tag(cfg, args.hash, args.name)

        elif args.tag_command == 'remove':
            rm_tag(cfg, args.hash, args.name)

    elif args.command == 'tier':
        if args.tier_command == 'set':
            set_tiers(cfg)

        elif args.tier_command == 'unset':
            unset_tiers(cfg)

        elif args.tier_command == 'activate':
            activate_tiers(cfg)

        elif args.tier_command == 'enforce':
            set_tiers(cfg)
            activate_tiers(cfg)

    elif args.command == 'tui':
        if args.action == 'show':
            if args.hash == 'all':
                print('WIP')
            elif args.hash == 'tier':
                print('WIP')
            else:
                curses_single(cfg, args.hash)

    elif args.command == 'clog':
        if args.action == 'set':
            set_clog(cfg)

        elif args.action == 'unset':
            unset_clog(cfg)

if __name__ == '__main__':
    main()