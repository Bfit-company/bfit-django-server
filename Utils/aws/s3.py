from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError

# from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


class S3:

    def __init__(self):

        self.s3 = boto3.resource('s3')
        self.s3_client = boto3.client('s3')

    def create_presigned_post(self, bucket, key, region_name='eu-central-1'):
        '''
        This function returns a presigned link and parameters for a POST request to upload file to S3.
        :param bucket: S3 bucket
        :param key: S3 key, including file name
        :param region_name: S3 region, default - eu-central-1
        :return: dictionary that contains the url and fields (parameters)
        '''
        s3_client = boto3.client('s3', region_name=region_name)
        try:
            response = s3_client.generate_presigned_post(Key=key,
                                                         Bucket=bucket,
                                                         Fields=None,
                                                         Conditions=None,
                                                         ExpiresIn=3600)
        except ClientError as e:
            print(e)
            return None
        # The response contains the presigned URL and required fields
        return response

    def create_presigned_get(self, bucket, key, region_name='us-east-2'):
        s3_client = boto3.client('s3', region_name=region_name)
        try:
            response = s3_client.generate_presigned_url(ClientMethod='get_object',
                                                        Params={
                                                            'Bucket': bucket,
                                                            'Key': key
                                                        })
        except ClientError as e:
            print(e)
            return None
        # The response contains the presigned URL and required fields
        return response

    def download_file(self, bucket, s3path, path):
        self.s3.Bucket(bucket).download_file(s3path, path)

    def upload_file(self, bucket, s3path, path):
        self.s3.Bucket(bucket).upload_file(path, s3path)

    def copy_file_to_new_bucket(self, source_bucket, source_key, target_bucket, target_key):
        source = {
            'Bucket': source_bucket,
            'Key': source_key
        }
        self.s3.meta.client.copy(source, target_bucket, target_key)

    @staticmethod
    def get_bucket_name_from_s3_path(s3_path_full_path):
        return urlparse(s3_path_full_path, allow_fragments=False).netloc

    @staticmethod
    def get_s3_key_from_s3_path(s3_path_full_path):
        parsed = urlparse(s3_path_full_path, allow_fragments=False)
        if parsed.query:
            return parsed.path.lstrip('/') + '?' + parsed.query
        else:
            return parsed.path.lstrip('/')

    def get_post_presigned_url(self,bucket,key):
        try:
          url = self.s3_client.generate_presigned_url(
                        ClientMethod="put_object",
                        Params={"Bucket":bucket, "Key":key},
                        ExpiresIn=3600
                    )
        except ClientError as e:
            print(e)
            return None
        return url

if __name__ == "__main__":


    s3 = S3()
    # s3 = boto3.client('s3')

    print(s3.create_presigned_get(bucket="bfit-data-storage",key="BANDANA.jpg"))