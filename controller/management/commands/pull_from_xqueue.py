import json
import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
import requests
import urlparse


log = logging.getLogger(__name__)


class Command(BaseCommand):
    args = "<queue_name>"
    help = "Pull items from given queues and send to grading controller"

    def handle(self, *args, **options):
        log.info(' [*] Pulling from xqueues...')
        flag=TRUE

        
        while flag:
            for queue_name in args:
                orphaned_submissions = Submission.objects.filter(queue_name=queue_name, push_time=None, return_time=None, retired=False)
                self.push_orphaned_submissions(orphaned_submissions)

    def login():
        '''
        Test Xqueue login behavior. Particularly important is the response for GET (e.g. by redirect)
        '''
        c = Client()
        full_login_url = urlparse.join(settings.XQUEUE_INTERFACE['url'],'/xqueue/login/')

        response = requests.post(login_url,{'username': settings.XQUEUE_INTERFACE['django_auth']['username'],
                                            'password':XQUEUE_INTERFACE['django_auth']['password']})
        (error,_) = parse_xreply(response.content)

        return error

    def push_orphaned_submissions(self, orphaned_submissions):
        for orphaned_submission in orphaned_submissions:
            current_time = timezone.now()
            time_difference = (current_time - orphaned_submission.arrival_time).total_seconds()
            if time_difference > settings.ORPHANED_SUBMISSION_TIMEOUT:

                log.info("Found orphaned submission: queue_name: {0}, lms_header: {1}".format(
                    orphaned_submission.queue_name, orphaned_submission.xqueue_header))
                orphaned_submission.num_failures += 1

                payload = {'xqueue_body': orphaned_submission.xqueue_body,
                           'xqueue_files': orphaned_submission.s3_urls}

                orphaned_submission.grader_id = settings.XQUEUES[orphaned_submission.queue_name]
                orphaned_submission.push_time = timezone.now()
                (grading_success, grader_reply) = _http_post(orphaned_submission.grader_id, json.dumps(payload), settings.GRADING_TIMEOUT)
                orphaned_submission.return_time = timezone.now()

                if grading_success:
                    orphaned_submission.grader_reply = grader_reply
                    orphaned_submission.lms_ack = post_grade_to_lms(orphaned_submission.xqueue_header, grader_reply)
                else:
                    log.error("Submission {} to grader {} failure: Reply: {}, ".format(orphaned_submission.id, orphaned_submission.grader_id, grader_reply))
                    orphaned_submission.num_failures += 1
                    orphaned_submission.lms_ack = post_failure_to_lms(orphaned_submission.xqueue_header)

                orphaned_submission.retired = True # NOTE: Retiring pushed submissions after one shot regardless of grading_success
                orphaned_submission.save()