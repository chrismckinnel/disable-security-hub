Disable SecurityHub
===================

Have you ever ran automation to enable SecurityHub in all accounts in all regions 
and then got whacked with a $150 bill at the end of the month?

SecurityHub charges can really add up!

You can use this script to disable SecurityHub in all of your accounts, in all 
regions.

Preparation
===========

1. Create a virtualenv or similar, and install the requirements with:

    $ pip install -r requirements.txt
    
2. Populate your ~/.aws/credentials file with profiles this script can use

E.g.,

    ~/.aws/credentials
    
    [dev_account]
    aws_access_key_id=
    aws_secret_access_key=
    aws_session_token=
    region=ap-southeast-2
    
    [test_account]
    aws_access_key_id=
    aws_secret_access_key=
    aws_session_token=
    region=ap-southeast-2
    
    [prod_account]
    aws_access_key_id=
    aws_secret_access_key=
    aws_session_token=
    region=ap-southeast-2

3. Copy config.tml.template to config.yml and update it with your IAM profiles and Security Hub Service Regions (from the regions we are disabling the service):

E.g., this is what it might look like if you're using AWS SSO:

    security_hub_master_account_profile: 111111111111_AWSAdministratorAccess
    security_hub_member_account_profiles:
      - 111111111112_AWSAdministratorAccess
      - 111111111113_AWSAdministratorAccess
      - 111111111114_AWSAdministratorAccess
      - 111111111115_AWSAdministratorAccess
      - 111111111116_AWSAdministratorAccess
      - 111111111117_AWSAdministratorAccess


Execution
=========

Run the script with:

    $ python disable_security_hub.py
    
    
The script will:

1.  Disassociate all member accounts from the master in all enabled regions
2.  Delete all member accounts from the master in all enabled regions
3.  Disable Security Hub in all member accounts, in all enabled regions
