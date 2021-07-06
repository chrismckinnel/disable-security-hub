#!/usr/bin/env python

import yaml
import boto3
import click
import logging

import botocore

from boto3.session import Session

logging.basicConfig(level=logging.INFO)
def disable_security_hub():
    logging.warn('This script will disassociate all member accounts and then '
                 'disable security hub completely in all accounts and all '
                 'regions defined in the config file!')
    proceed = click.prompt('Proceed?', type=bool)

    if not proceed:
        logging.info('Not proceeding!')
        return
    
    config = get_config()
    member_account_ids = get_member_account_ids(config=config)
    disassociate_member_accounts_from_master(
        profile_name=config.get('security_hub_master_profile'),
        account_ids=member_account_ids
    )
    delete_member_accounts_from_master(
        profile_name=config.get('security_hub_master_profile'),
        account_ids=member_account_ids
    )
    profile_names = config.get('security_hub_member_profiles')
    disable_security_hub_in_member_accounts(profile_names=profile_names)
    
    
def disable_security_hub_in_member_accounts(profile_names):
    logging.info('Disabling Security Hub in all Member accounts')
    config = get_config()
    for profile_name in profile_names:
        for region_name in config.get('regions'):
            disable_security_hub_in_region(
                profile_name=profile_name, 
                region_name=region_name
            )
def get_master_account_session(region_name, profile_name):
    return Session(
        region_name=region_name, 
        profile_name=profile_name
    )

            
def disassociate_member_accounts_from_master(profile_name, account_ids):
    config = get_config()
    for region_name in config.get('regions'):
        session = get_master_account_session(
            region_name=region_name,
            profile_name=profile_name
        )
        security_hub_client = session.client('securityhub')
        
        logging.info('Disassociating all member accounts from master for '
                     'region %s' % region_name)
        try:
            security_hub_client.disassociate_members(AccountIds=account_ids)
        except botocore.exceptions.ClientError as exception:
            if exception.response['Error']['Code'] == 'UnrecognizedClientException':
                logging.info('Ignoring region %s, probably not enabled' % region_name)
    
    
def delete_member_accounts_from_master(profile_name, account_ids):
    config = get_config()
    for region_name in config.get('regions'):
        session = get_master_account_session(
            region_name=region_name,
            profile_name=profile_name
        )
        security_hub_client = session.client('securityhub')
        
        logging.info('Deleting all member accounts from master for '
                     'region %s' % region_name)
        try:
            security_hub_client.delete_members(AccountIds=account_ids)
        except botocore.exceptions.ClientError as exception:
            if exception.response['Error']['Code'] == 'UnrecognizedClientException':
                logging.info('Ignoring region %s, probably not enabled' % region_name)


def get_member_account_ids(config):
    logging.info('Getting all member account IDs from profiles in config')
    return [
        get_account_id_from_profile(profile_name=profile_name)
        for profile_name in config.get('security_hub_member_profiles')
    ]
def get_account_id_from_profile(profile_name):
    session = Session(
        profile_name=profile_name
    )
    sts_client = session.client('sts')
    response = sts_client.get_caller_identity()
    return response['Account']


def disable_security_hub_in_region(profile_name, region_name):
    logging.info('Disabling SecurityHub for %s in %s '
                 'region' % (profile_name, region_name))
    session = Session(
        region_name=region_name, 
        profile_name=profile_name
    )
    security_hub_client = session.client('securityhub')
    try:
        security_hub_client.disable_security_hub()
    except botocore.exceptions.ClientError as exception:
        if exception.response['Error']['Code'] == 'UnrecognizedClientException':
            logging.info('Ignoring region %s, probably not enabled' % region_name)
def get_config():
    with open('config.yml') as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config

if __name__ == '__main__':
    disable_security_hub()