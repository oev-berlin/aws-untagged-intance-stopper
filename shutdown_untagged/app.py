import json
import boto3
import sys

def get_ec2_client(region):
    """ returns an ec2 client in the specified region """
    ec2 = boto3.client('ec2', region_name=region)
    return ec2

def get_regions():
    """ returns every aws regon code """
    regions = []
    ec2 = get_ec2_client("eu-central-1")
    ec2_response = ec2.describe_regions()

    for resp in ec2_response['Regions']:
        regions.append(resp['RegionName'])
    
    return(regions)


def get_all_instances(region):
    """ returns all instances from one region """
    all_instances = []
    ec2 = get_ec2_client(region)
    response = ec2.describe_instances()

    for instances in response['Reservations']:
        all_instances.append(instances['Instances'][0]['InstanceId'])
    return all_instances

def get_perm_instances(region):
    """ returns all running untagged instances """
    perm_instances = []
    ec2 = get_ec2_client(region)
    response = ec2.describe_instances(
        Filters = [
            {
                'Name': 'tag:running',
                'Values': [
                    'perm'
                ]    
            }
        ]
    )
    for instances in response['Reservations']:
        perm_instances.append(instances['Instances'][0]['InstanceId'])

    return perm_instances

def diff_list(list1, list2):
    """ returns the difference between two lists """

    return(list(set(list1) - set(list2)))

def get_untagged_instances(region):
    """ takes the list of all instances and removes the tagged once 
    then return only the untagged instances """

    all_instances = get_all_instances(region)
    all_perm_instances = get_perm_instances(region)
    all_untagged_instances = diff_list(all_instances, all_perm_instances)

    return all_untagged_instances

def stop_instances(list_of_instances, region):
    """ stops all provided instances """

    ec2 = get_ec2_client(region)
    for instance in list_of_instances:
        try:
            response = ec2.stop_instances(
                InstanceIds = [
                    instance
                ]
            )
            print(instance + " " + response['StoppingInstances'][0]['CurrentState']['Name'] + " in region " + region)
        except:
            print('Error: ', sys.exc_info()[0])

def lambda_handler(event, context):
    """ main function """
    try:
        for region in get_regions():
            stop_instances(get_untagged_instances(region), region)

        return {
            "statusCode": 200,
            "body": "successfully shutted down all untagged instances",
        }
    except:
        return {
            "statusCode": 400,
            "body": "unknown error"
        }