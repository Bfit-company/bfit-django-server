from dotenv import load_dotenv
import os
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# S3
S3_KEY = 'users/user={user}/{image_type}/ts_day={ts_day}/{filename}'
BUCKET = os.getenv('BUCKET', 'bfit-data-storage')
