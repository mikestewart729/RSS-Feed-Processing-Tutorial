# podcasts/management/commands/startjobs.py

import feedparser
from django.core.management.base import BaseCommand
from dateutil import parser
from podcasts.models import Episode

# From stackexchange
import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# Back to tutorial
def save_new_episodes(feed):
    """
    Saves new episodes to the database. Checks against the guid of episodes currently
    in the database, and if not, saves it to the database.

    Args:
       feed (feedparser): feedparser object for parsing
    """
    podcast_title = feed.channel.title
    podcast_image = feed.channel.image["href"]

    for item in feed.entries:
        print(item.title)
        if not Episode.objects.filter(guid=item.guid).exists():
            episode = Episode(
                title=item.title,
                description=item.description,
                pub_date=parser.parse(item.published),
                link=item.links[0],
                image=podcast_image,
                podcast_name=podcast_title,
                guid=item.guid,
            )
            episode.save()

def fetch_ywa_episodes():
    """ Fetches new You're Wrong About episodes from RSS feed. """
    _feed = feedparser.parse("https://feeds.buzzsprout.com/1112270.rss")
    save_new_episodes(_feed)

def fetch_maintenancephase_episodes():
    """ Fetches new Maintenance Phase episodes from RSS feed. """
    _feed = feedparser.parse("https://feeds.buzzsprout.com/1411126.rss")
    save_new_episodes(_feed)

def fetch_bastards_episodes():
    """ Fetches new Behind the Bastards episodes from RSS feed. """
    _feed = feedparser.parse("https://feeds.megaphone.fm/behindthebastards")
    save_new_episodes(_feed)

class Command(BaseCommand):
    def handle(self, *args, **options):
        fetch_ywa_episodes()
        fetch_maintenancephase_episodes()
        fetch_bastards_episodes()
