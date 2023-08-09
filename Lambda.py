import json
import boto3
import base64

# A low-level client representing Amazon Simple Storage Service (S3)
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input (You may also check lambda test)
    key = event['s3_key']                               ## TODO: fill in
    bucket = event['s3_bucket']                         ## TODO: fill in

    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    s3.download_file(bucket, key, "/tmp/image.png")

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:          # Read binary file
        image_data = base64.b64encode(f.read())      # Base64 encode binary data ('image_data' -> class:bytes)

    # Pass the data back to the Step Function
    print("Event:", event.keys())


    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,      # Bytes data
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }


"""
ImageClassifier : Lambda function to predict image classification
"""
import os
import io
import boto3
import json
import base64

# setting the  environment variables
ENDPOINT_NAME = 'image-classification-2023-06-22-00-27-43-585'
# We will be using the AWS's lightweight runtime solution to invoke an endpoint.
runtime= boto3.client('runtime.sagemaker')

def lambda_handler(event, context):
    print(event)
    # Decode the image data
    imdata = event['body']['image_data']
    image = base64.b64decode(imdata)

    # Make a prediction:
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
                                       ContentType='image/png',
                                       Body=image)

    # We return the data back to the Step Function
    event["inferences"] = json.loads(response['Body'].read().decode('utf-8'))
    return {
        'statusCode': 200,
        'body': event
    }

"""
InferenceConfidenceFilter : Lambda function tofiter inference results based on confidence
"""
import json


THRESHOLD = 0.7

def lambda_handler(event, context):
    # Get the inferences from the event
    inferences = event['body']['inferences']

    # Check if any values in any inferences are above THRESHOLD
    meets_threshold = (max(inferences) > THRESHOLD)

    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': event
    }
