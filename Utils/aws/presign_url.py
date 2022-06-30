import os
import json
import logging
import requests
from rest_framework.response import Response
import boto3
from botocore.exceptions import ClientError
from Utils.utils import Utils
from rest_framework.views import APIView
from django.http import HttpResponse
from Utils.aws.s3 import S3
BUCKET = os.getenv('BUCKET', 'bfit-data-storage')
KEY = 'users_images/user={user}/{image_type}/ts_day={ts_day}/{filename}'
s3 = S3()

class PresignUrl(APIView):
    def post(self, request):

        filename = request.data.get('filename')
        user = request.data.get('user')
        image_type = request.data.get('image_type')

        key = KEY.format(
            user=user,
            image_type=image_type,
            ts_day=Utils.get_ts_today(),
            filename=filename
        )
        key = f's3://bfit-data-storage/BANDANA.jpg'
        # url = s3.create_presigned_post(BUCKET,key,region_name="us-east-2")
        try:
            s3_client = boto3.client('s3',)
            url = s3_client.generate_presigned_url(
                ClientMethod="put_object",
                Params={"Bucket":BUCKET,"Key":key},
                ExpiresIn=3600
            )
        except ClientError:
            raise

        # with open("/Users/liadhazoot/BFIT/BfitServer/Utils/aws/a1.jpeg", 'rb') as file_to_upload:
        files = {"file": open("/Users/liadhazoot/BFIT/BfitServer/Utils/aws/a1.jpeg", 'rb')}
        upload_response = requests.post(url,  files=files)
        print(upload_response.status_code)
        return Response(upload_response)
        # return Response({
        #     'statusCode': 201,
        #     'headers': {
        #         'Access-Control-Allow-Headers': 'Content-Type',
        #         'Access-Control-Allow-Origin': '*',
        #         'Access-Control-Allow-Methods': 'OPTIONS,GET'
        #     },
        #     'body': json.dumps(
        #         {
        #             'bucket': BUCKET,
        #             'key': key,
        #             'link': url
        #         }
        #     )
        # },status=201)

    def get(self, request):
        return HttpResponse("hello world", status=200)