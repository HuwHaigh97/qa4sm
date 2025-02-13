from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils import timezone
from validator.models import ValidationRun


class Command(BaseCommand):
    help = "Deletes all validation runs that are older than 30 days ONLY if they have not been published or archived."

    def handle(self, *args, **kwargs):
        oneMonthAgo = timezone.now() - timedelta(days=30)
        oldRuns = ValidationRun.objects.filter(start_time__lt=oneMonthAgo, is_archived=False, doi__exact='', isRemoved=False)

        for run in oldRuns:
            if not run.isRemoved and not run.is_archived and run.doi == '':
                run.isRemoved = True
                run.save()

        self.stdout.write(f"Marked {oldRuns.count()} old validation runs as removed.")