#!/usr/bin/env python3
from bs4 import BeautifulSoup as bs
import requests

import shutil
import tempfile
import re
import logging
import argparse
import textwrap
import time
import os

logger = logging.getLogger(__name__)


def download_file(url: str, filename: str= '') -> None:
    """Download a file using requests
    :param url: A URL specifying the file to download
    :param filename: A legal path and filename to save to

    Was adapted from https://stackoverflow.com/a/35844551
    """
    logger.debug(f"Downloading '{url}', to '{filename}'")

    r = requests.get(url, stream=True)
    with tempfile.NamedTemporaryFile(delete=False) as file:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                # filter out keep-alive new chunks
                file.write(chunk)
        file.flush()

    # Overwrite if exists
    shutil.move(file.name, filename)


def make_filename(url: str, title: str) -> str:
    """Uses information from url and title to form a nice filename
    :param url: A URL pointing to a SU video file
    :param title: A SU title
    :return: S00E00 Title.extension
    """
    try:
        file_name, extension = url.split('/')[-1].split('.')
        # Use regex to get season and episode numbers, matches s1e1
        regex = re.match('\A(short)?s(?P<season>[0-9]+)e(?P<episode>[0-9]+)', file_name.lower())

        # Remove illegal filename characters
        title = re.sub('["/<>|*.]+', '', title)
        # Remove prefix
        title = re.match("[0-9]+\.?\s(?P<title>[0-9a-zA-Z\s']+)", title).group('title')

        # Combine everything in format of S00E00 Title.extension
        return f'S{regex.group("season").zfill(2)}E{regex.group("episode").zfill(2)} {title.title()}.{extension}'
    except AttributeError:
        # Oops, some regex failed!
        logger.warning(f"Failed to= make filename for url='{url}, title='{title}'")
        # Return filename from URL
        return url.split('/')[-1]


def download_all(html: str, overwrite: bool) -> None:
    """Download all the SU episodes to be found in the supplied html.
    :param html: HTML of http://stevenuniver.se
    :param overwrite: Delete existing material on name collision?
    """
    global stats
    soup = bs(html, 'lxml')

    # Get the seasons
    seasons = soup.select('div.accordion.ui-accordion.ui-widget.ui-helper-reset')
    logger.info(f'Seasons found: {len(seasons)}')

    for season in seasons:
        # Get time for statistics
        ts = time.perf_counter()

        # Get season title
        season_title = season.findPrevious('h1').text.lower()

        # Show progress
        logger.info(f"Working on '{season_title}'.")

        videos = season.find_all('source')
        stats['total_episodes'] += len(videos)
        logger.debug(f"Videos found: {len(videos)}")

        # TODO: Maybe make it optional to save each season in a subdirectory
        if not os.path.isdir(season_title):
            logger.debug(f"Dir '{season_title}' created.")
            os.mkdir(season_title)

        for video in videos:
            # Get video title
            video_title = video.parent.findPrevious('h3').text.lower()
            # Get source URL
            src_url = video['src']
            if not str(src_url).endswith('.mp4'):
                logger.warning(f"Unfamiliar file type found at '{src_url}', with title '{video_title}''")

            # Make filename and combine with season directory to form path
            filename = make_filename(src_url, video_title)
            path = os.path.join(season_title, filename)

            if os.path.exists(path) and not overwrite:
                # File exists, but overwrite is False
                logger.debug(f"Skipping '{video_title}'")
            else:
                # Initiate download
                download_file(src_url, path)
                logger.info(f"{filename} has finished downloading.")

                # Save some data for statistics
                stats['total_downloads'] += 1
                stats['total_size_MB'] += os.path.getsize(path) / 1000000
            te = time.perf_counter()
            stats['total_time_sec'] += (te - ts)


if __name__ == '__main__':
    # Setup argparse
    parser = argparse.ArgumentParser(description='A simple CLI for downloading Steven Universe episodes.',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent("""\
                                     Steven Universe Downloader
                                     --------------------------
                                     Please make sure requests, BeautifulSoup4 and lxml are installed.
                                     Beware! http://stevenuniver.se runs a cryptominer in the background."""))
    parser.add_argument('source', type=str,
                        help='Path to local copy of http://stevenuniver.se',
                        default='')
    # Optional commandline flags
    parser.add_argument('-o', '--overwrite', help='Overwrite existing files, default=False',
                        action='store_true')
    parser.add_argument('-v', '--verbose', help='Increase output verbosity',
                        action='store_true')
    args = parser.parse_args()

    # Setup logging handler
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()

    ch.setLevel(logging.INFO)
    if args.verbose:
        ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    # Get HTML
    with open(args.source, 'r') as file:
        html = file.read()
        if 'coinhive' in html:
            # BeautifulSoup does NOT execute javascript, so we should be fine.
            logger.warning('HTML still contains coinhive script, please beware!')

    try:
        stats = {'total_episodes': 0, 'total_downloads': 0, 'total_size_MB': 0, 'total_time_sec': 0}
        download_all(html, overwrite=args.overwrite)
    except KeyboardInterrupt:
        logger.error("Program interrupted by user")
    finally:
        # TODO: Transform units when numbers get large enough.
        average_speed = stats['total_size_MB'] / stats['total_time_sec']
        logger.info(f"Downloaded {stats['total_downloads']} episodes in {stats['total_time_sec']:.1f}sec. "
                    f"Total size {stats['total_size_MB']:.1f}MB, average speed {average_speed:.1f}MB/sec")
