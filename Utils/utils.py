import re

import phonenumbers as phonenumbers
from django.db.models import Q
from datetime import datetime, timezone

from Utils.aws.presign_url import PresignUrl
from Utils.aws.s3 import S3
from config import S3_KEY, BUCKET
from job_type_app.models import JobTypeDB
from person_app.models import PersonDB
from phonenumbers import parse, is_valid_number


class Utils:

    @staticmethod
    def get_detail_by_list_id(table, query_list_id, attribute):
        my_filter_qs = Q()
        for query in query_list_id:
            my_filter_qs = my_filter_qs | Q(id=query[attribute])

        return table.objects.filter(my_filter_qs)

    @staticmethod
    def get_now_as_timestamp():
        return int(datetime.now().timestamp())

    @staticmethod
    def get_day_ts(ts):
        x = datetime.fromtimestamp(ts, tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        return int(datetime.timestamp(x))

    @staticmethod
    def get_ts_today():
        ts_now = int(datetime.timestamp(datetime.now()))
        return Utils.get_day_ts(ts_now)

    @staticmethod
    def get_job_type_name(job_list: list):
        job_name_list = []
        for job in list(JobTypeDB.objects.filter(pk__in=job_list)):
            job_name_list.append(job.name)

        return job_name_list

    @staticmethod
    def save_profile_img_to_s3(file, email, person_id):
        try:
            s3 = S3()
            s3_key = S3_KEY.format(
                user=email,
                image_type="profile_image",
                ts_day=Utils.get_ts_today(),
                filename=file.name
            )
            s3.upload_file_obj(file=file, bucket=BUCKET, s3_key=s3_key)
            s3_path = f's3://{BUCKET}/{s3_key}'
            PersonDB.objects.filter(pk=person_id).update(profile_image_s3_path=s3_path)
            return PresignUrl().create_presigned_url(s3_path)
        except Exception as ex:
            raise ex

    @staticmethod
    def profile_img_s3_path(file, email):
        try:
            s3 = S3()
            s3_key = S3_KEY.format(
                user=email,
                image_type="profile_image",
                ts_day=Utils.get_ts_today(),
                filename=file.name
            )
            s3.upload_file_obj(file=file, bucket=BUCKET, s3_key=s3_key)
            s3_path = f's3://{BUCKET}/{s3_key}'
            return s3_path
        except Exception as ex:
            raise ex

    @staticmethod
    def is_phone_number_valid(phone_number):
        try:
            if (re.search('[a-zA-Z]', phone_number)):
                raise Exception
            parsed_phone_number = parse(phone_number, None)
            if not is_valid_number(parsed_phone_number):
                raise Exception
            return True
        except:
            return False
