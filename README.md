# dynamodb-provisioner-cli

Target Audience:

This Python script is purposed for operational needs where DynamoDB capacity needs to be spun up and down on-demand without having to rely 100% on the native autoscaling that AWS offers. This program
is perfect for those environments with bursty DynamoDB writes or where your workloads are predictable. Alternatively this can simply be used for Administrative purposes where you'd like to be notified when a table has been successfuly scaled and pass that state to another system in order to proceed with your application logic.


Why aren't you using the AWS CLI:

Good Question :) - In a nutshell when using the AWS CLI an asynchronous API call is made to DynamoDB (UpdateTable) that won't return a success or fail due to the time being completely dependent on the size of a customers table.
In the past for my personal use this program came in handy for spikey predictable writes made to DynamoDB where AWS auto-scaling wasn't reacting quickly enough. I.E if you expect a bulk write to DynamoDB everyday at 1PM EST you can setupa cron-like schedule to run this program in order to "pre-warm" your tables before your application queries/writes DynamoDB. Overall if you can't simply fire off a scale operation with your DynamoDB table and want to track the state of it's progress than this is likely to be helpful.
