import json
import os
from urllib import request
import logging

# Retrieve environment variables
VIDEO_BUCKET = os.environ.get('VIDEO_BUCKET')
TRANSLATE_BUCKET = os.environ.get('TRANSLATE_BUCKET')
CAPTION_API = os.environ.get('CAPTION_API')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def lambda_handler(event, context):
    logger.info('Lambda handler started')

    response = {
        'statusCode': 200,
        'body': json.dumps('Hello from Caption Lambda!')
    }

    try:
        if event:
            file_obj = event['Records'][0]
            bucket_name = str(file_obj['s3']['bucket']['name'])
            file_name = str(file_obj['s3']['object']['key'])

            logger.info(f"Processing file: {file_name} from bucket: {bucket_name}")

            _, file_name = os.path.split(file_name)
            file_name, _ = os.path.splitext(file_name)
            video_id = file_name.replace('-pt', '')

            original_video = '{}/original/{}.mp4'.format(VIDEO_BUCKET, video_id)
            transcription = '{}/en/{}-en.vtt'.format(TRANSLATE_BUCKET, video_id)
            translation = '{}/pt/{}-pt.vtt'.format(TRANSLATE_BUCKET, video_id)
            captioned_video = '{}/captioned/{}.mp4'.format(VIDEO_BUCKET, video_id)
            job_info = '{}/info/{}.json'.format(VIDEO_BUCKET, video_id)

            logger.info("Generated paths for video processing")

            data = {
                'original_video': original_video,
                'transcription': transcription,
                'translation': translation,
                'captioned_video': captioned_video,
                'job_info': job_info
            }
            url = 'http://{}:8080/video'.format(CAPTION_API)

            req = request.Request(url)
            req.add_header('Content-Type', 'application/json; charset=utf-8')
            data = json.dumps(data)
            data = data.encode('utf-8')
            req.add_header('Content-Length', len(data))

            logger.info(f"Sending request to captioning API at {url}")
            response = request.urlopen(req, data)
            logger.info("Request to captioning API completed successfully")

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        response = {
            'statusCode': 500,
            'body': json.dumps(f"Error processing file: {e}")
        }

    return response
