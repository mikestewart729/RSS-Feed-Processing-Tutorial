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
class Command(BaseCommand):
    def handle(self, *args, **options):
        feed = feedparser.parse("https://realpython.com/podcasts/rpp/feed")
        podcast_title = feed.channel.title
        podcast_image = feed.channel.image["href"]

        for item in feed.entries:
            print(item.title)
            if not Episode.objects.filter(guid=item.guid).exists():
                episode = Episode(
                    title=item.title,
                    description=item.description,
                    pub_date=parser.parse(item.published),
                    link=item.link,
                    image=podcast_image,
                    podcast_name=podcast_title,
                    guid=item.guid,
                )
                episode.save()
