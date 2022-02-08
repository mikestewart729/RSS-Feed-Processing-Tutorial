# podcasts/management/commands/startjobs.py

#Standard library
import logging

# Django
from django.conf import settings
from django.core.management.base import BaseCommand

# Third party
import feedparser
from dateutil import parser
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

# Models
from podcasts.models import Episode

# From stackexchange
import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# Back to tutorial
logger = logging.getLogger(__name__)

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

def delete_old_job_executions(max_age=604_800):
    """ Deletes execution logs older than max_age. """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

class Command(BaseCommand):
    help = 'Runs apscheduler.'

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            fetch_ywa_episodes,
            trigger="interval",
            minutes=2,
            id="You're Wrong About Podcast",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: You're Wrong About Podcast.")

        scheduler.add_job(
            fetch_maintenancephase_episodes,
            trigger="interval",
            minutes=2,
            id="Maintenance Phase Podcast",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: Maintenance Phase Podcast.")

        scheduler.add_job(
            fetch_bastards_episodes,
            trigger="interval",
            minutes=2,
            id="Behind the Bastards Podcast",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: Behind the Bastards Podcast.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="Delete old job executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: Delete old job executions.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
