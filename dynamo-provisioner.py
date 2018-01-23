import socket
import boto3
import requests
import json
import sys
import argparse
import time
client = boto3.client('dynamodb')

# Define CLI arguments as opposed to hard-coding values passed to functions.

parser = argparse.ArgumentParser(description='Pass in parameters for DynamoDB')
parser.add_argument('--table-name', metavar='T', type=str, help='The name of your DynamoDB table', required=True)
parser.add_argument('--write-capacity-units', metavar='wcu', type=int, help='The number of write-capacity-units you would like', required=True)
parser.add_argument('--read-capacity-units', metavar='rcu', type=int, help='The number of read-capacity-units you would like', required=True)
args = parser.parse_args()

# Define Global variables via user-input

table = args.table_name

wcu = args.write_capacity_units

rcu = args.read_capacity_units

print "You've passed in the following params: " + "DynamoDB Table " +  table + " Will be configured at " + str(wcu) + " Write Capacity Unit(s) " + "& " + str(rcu) + " Read Capacity Unit(s) "

# Get Meta-Data for auditing (Assuming the Script will be called from a service such as AWS Batch - We can alternatively call the meta-data endpoint of a respective EC2 instance and pull information such as the instance-id.

client_fqdn = socket.getfqdn()


def send_slack_message(table,data):
	webhook_url = 'https://hooks.slack.com/YOURWEBHOOKHERE'
	response = requests.post(webhook_url, data=json.dumps(data),
    	headers={'Content-Type': 'application/json'})
	if response.status_code !=200:
		print "An error occured while attempting to POST to Slack. Please make sure the webhook and Slack API is healthy"
		print " Here's the response: " + str(response)

def dynamo_monitor_update(table):
	response = client.describe_table(TableName=table)
	table_status = response['Table']['TableStatus']
	if table_status == 'UPDATING':
		print "DynamoDB Table: " + table + " Is still having it's capacity provisioned. Sleeping for 10 seconds"
		time.sleep(10)
		dynamo_monitor_update(table)
	elif table_status == 'ACTIVE':
		print "DynamoDB Table: " + table + " has successfully been updated"
                data = {"text": "DynamoDB Table: " + table + " has been successfully updated by " + str(client_fqdn) + " to " + str(wcu) + " Write-Capacity-Units" + " and " + str(rcu) + " Read-Capacity-Units", "username": "dynamo-provisioner-tool", "channel": "#engineering"}  
		send_slack_message(table,data)
	else:
		print "An error has occured with the status of the table: " + response
		

def dynamo_scale_table(table,wcu,rcu):
	response = client.update_table(TableName=table,ProvisionedThroughput={'WriteCapacityUnits': wcu, 'ReadCapacityUnits': rcu})
        dynamo_monitor_update(table)

def dynamo_table_stats(table,wcu,rcu):
	response = client.describe_table(TableName=table)
	table_status = response['Table']['TableStatus']
	if table_status == 'ACTIVE':
		print table + " Is elgible for a provisioning update "
                dynamo_scale_table(table,wcu,rcu) 
        elif table_status == 'UPDATING':
		print table + " Is currently being updated already and cannot be provisioned further until the previous update is fulfilled "
		data = {"text": "DynamoDB Table: " + table + " is already processing a provisioning update by " + str(client_fqdn), "username": "dynamo-provisioner-tool", "channel": "#engineering"}
                send_slack_message(table,data)
	else: 
		print table + " Couldn't be queried for status. Here's the raw response from DynamoDB: " + response
		data = {"text": "Couldn't detect a table-status for DynamoDB Table: " + table + " Here's the raw error: " + str(response), "username": "dynamo-provisioner-tool", "channel": "#engineering"}
                send_slack_message(table,data)


dynamo_table_stats(table,wcu,rcu)
