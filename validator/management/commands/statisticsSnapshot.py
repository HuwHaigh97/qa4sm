from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from django.db.models import Count, Sum

from validator.models.custom_user import User
from validator.models.validation_run import ValidationRun
from validator.models.snapshots import snapshot
from validator.models.user_dataset_file import UserDatasetFile

class Command(BaseCommand):
    help = "Create a snapshot of user statistics at regular intervals."

    def handle(self, *args, **kwargs):
        today = now().date()
        previous = today - timedelta(days=1)
        print(previous)
        user_registrations = User.objects.filter(date_joined__date = today).count()
        user_deactivations = User.objects.filter(date_joined__date__lte = previous).count() - User.objects.count() + user_registrations

        submitted_validations = ValidationRun.objects.filter(start_time__date = today).filter(isRemoved = False)

        nValidations = submitted_validations.count()
        nSuccessful = submitted_validations.filter(status='DONE').count()

        uploadedFiles = UserDatasetFile.objects.filter(upload_date__date = today)
        nUploaded = uploadedFiles.count()
        totalUpload = sum(file.file_size for file in uploadedFiles) 

        todaySnapshot, created = snapshot.objects.get_or_create(
            date=today,
            defaults={
                'newAccounts': user_registrations,
                'nValidations_submitted': nValidations,
                'nSuccessfulValidations': nSuccessful,
                'deactivatedAccounts': user_deactivations,
                'nFiles_uploaded': nUploaded,
                'total_uploadSize': totalUpload,
                }
        )

        #if not created: 
        #    todaySnapshot.user_registrations = user_registrations
        #    todaySnapshot.jobs_run = submitted_validations
        #    todaySnapshot.save()
        if created:
            self.stdout.write(self.style.SUCCESS(f"Successfully updated daily snapshot for {today}: {user_registrations} new accounts, {user_deactivations} deactivated accounts, {nValidations} validations submitted, {nUploaded} files uploaded, {totalUpload*(1/1024)} mb total."))