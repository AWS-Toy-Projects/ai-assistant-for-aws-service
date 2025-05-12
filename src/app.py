import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

# Initialize Bedrock client
bedrock_runtime = boto3.client('bedrock-runtime')
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')

def lambda_handler(event, context):
    """
    Lambda function handler for Bedrock Agent action group.
    This function processes requests from the Bedrock Agent and returns appropriate responses.
    
    Args:
        event (dict): Lambda function invocation event
        context (LambdaContext): Lambda function context
    
    Returns:
        dict: Response containing action results
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract request information from the event
        action_group = event.get('actionGroup', '')
        api_path = event.get('apiPath', '')
        parameters = event.get('parameters', [])
        request_body = event.get('requestBody', {})
        prompt = request_body.get('prompt', '')
        
        # Convert parameters to a more usable dictionary format
        param_dict = {}
        for param in parameters:
            if 'name' in param and 'value' in param:
                param_dict[param['name']] = param['value']
        
        logger.info(f"Action Group: {action_group}, API Path: {api_path}")
        logger.info(f"Parameters: {param_dict}")
        
        # Process the request based on the action group and API path
        if action_group == "SampleActionGroup":
            if api_path == "/getServiceInfo":
                service_name = param_dict.get('serviceName', '')
                return get_service_info(prompt)
        
        # Default response if no matching action is found
        return {
            "response": {
                "message": "Action not supported"
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            "response": {
                "error": str(e)
            }
        }

def get_service_info(prompt):
    """
    Get information about an AWS service using Bedrock model.
    
    Args:
        service_name (str): Name of the AWS service
    
    Returns:
        dict: Response containing service information
    """
    try:
        # Use Bedrock model to get information about the service
        
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(response.get('body').read())
        service_info = response_body.get('content', [{}])[0].get('text', 'No information available')
        
        return {
            "response": {
                "prompt": prompt,
                "information": service_info
            }
        }
        
    except ClientError as e:
        logger.error(f"Error invoking Bedrock model: {str(e)}")
        return {
            "response": {
                "error": f"Failed to get information: {str(e)}"
            }
        }