"""
Django command to wait for the database to be ready before starting the server.
"""
from django.core.management.base import BaseCommand

import time

from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error


class Command(BaseCommand):
    """Wait for the database to be ready before starting the server."""

    def handle(self, *args, **optons):
        self.stdout.write('Waiting for database...')
        db_up = False
        while db_up is False:
            # Check if the database is available
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database is ready!'))
