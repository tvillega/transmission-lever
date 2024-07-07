# /usr/bin/env python

from core.label import find_label, find_regex_label, sw_label, rm_label
from core.client import get_client, get_torrents_list, start_torrent
from core.torrent import change_upload_throttle


def upd_tier(num: str,
             config: dict,
             torrent_hash: str
             ) -> None:

    """
    Change the label of a tier
    :param num: the number of the tier
    :param config: valid configuration dictionary
    :param torrent_hash: hash of a single torrent
    :return: None
    """

    client = get_client(config)
    prefix_char = config['General']['prefix']['tiers']
    new_label = prefix_char + "tier-" + num
    old_label = prefix_char + "tier-" + str(int(num) - 1)

    sw_label(client, torrent_hash, old_label, new_label)
    limits = config['Tiers'][num]
    change_upload_throttle(client, torrent_hash, limits)


def set_tiers(config: dict) -> None:
    """
    Set bandwidth limits through tier labels
    :param config: valid configuration dictionary
    :return: None
    """

    client = get_client(config)
    prefix = config['General']['prefix']['tiers'] + "tier-"

    for torrent in get_torrents_list(client):
        ratio = torrent.ratio
        torrent_hash = torrent.hashString
        free = find_label(client, torrent_hash, prefix+"free")
        progress = torrent.progress

        # Check if torrent is complete
        if progress != 100:
            continue

        # Maintain Tier free
        elif free:
            limits = config['Tiers']["free"]
            change_upload_throttle(client, torrent_hash, limits)

        # Set Tier 0
        elif ((ratio >= 0)
              and (ratio < config["Tiers"]["0"]["seed_ratio_limit"])):
            upd_tier("0", config, torrent_hash)

        # Set Tier 1 to max num
        else:
            for i in range(1, config['General']['tiers']['number']+1):
                new_num = str(i)
                old_num = str(i - 1)
                if ((ratio >= config["Tiers"][old_num]["seed_ratio_limit"])
                        and (ratio < config["Tiers"][new_num]["seed_ratio_limit"])):
                    upd_tier(new_num, config, torrent_hash)
                    break

            else:
                print(f"Ratio {ratio} out of bounds for torrent with hash {torrent_hash}")


def unset_tiers(config: dict) -> None:

    """
    Remove tier labels and reset upload limits
    :param config: valid configuration dictionary
    :return: None
    """

    client = get_client(config)
    prefix_char = config['General']['prefix']['tiers']
    tiers_num = config['General']['tiers']['number']
    upper_limit = tiers_num+1

    for torrent in get_torrents_list(client):
        torrent_hash = torrent.hashString

        for i in range(0, upper_limit):
            tier_label = prefix_char + "tier-" + str(i)
            exists = find_regex_label(client, torrent_hash, tier_label)

            if exists:
                rm_label(client, torrent_hash, tier_label)
                limits = config['Tiers']["free"]
                change_upload_throttle(client, torrent_hash, limits)
                break


def activate_tiers(config: dict) -> None:

    """
    Resume paused torrent managed by the tier tags
    :param config: valid configuration dictionary
    :return: None
    """

    client = get_client(config)
    prefix_char = config['General']['prefix']['tiers']
    tiers_num = config['General']['tiers']['number']
    upper_limit = tiers_num+1

    for torrent in get_torrents_list(client):
        torrent_hash = torrent.hashString

        for i in range(0, upper_limit):
            tier_label = prefix_char + "tier-" + str(i)
            exists = find_regex_label(client, torrent_hash, tier_label)

            if exists:
                if torrent.status == 'stopped':
                    start_torrent(client, torrent_hash)
                    break
