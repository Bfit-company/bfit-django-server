import os
import json
import logging
import requests
from rest_framework.response import Response
import boto3
from botocore.exceptions import ClientError
from rest_framework.views import APIView
from django.http import HttpResponse
from Utils.aws.s3 import S3
from config import S3_KEY, BUCKET

s3 = S3()

class PresignUrl(APIView):
    @staticmethod
    def create_presigned_url(s3_path):
        return s3.create_presigned_get(bucket=s3.get_bucket_name_from_s3_path(s3_path),
                                    key=s3.get_s3_key_from_s3_path(s3_path))


    # def post(self, request):
    #
    #     filename = request.data.get('filename')
    #     user = request.data.get('user')
    #     image_type = request.data.get('image_type')
    #
    #     key = S3_KEY.format(
    #         user=user,
    #         image_type=image_type,
    #         ts_day=Utils.get_ts_today(),
    #         filename=filename
    #     )
    #     url = s3.get_post_presigned_url(bucket=BUCKET,key=key)
    #
    #     return Response({"s3_path":os.path.join("s3://",BUCKET,key),"url": url}, status=200)
    #
    # def get(self, request):
    #
    #     s3_path = request.query_params.get("s3_path")
    #     url = self.create_presigned_url(s3_path)
    #     if url:
    #         return Response({"url": url}, status=200)
    #     else:
    #         return Response({"error": "there is a problem with getting the s3 presigned url"},status=400)