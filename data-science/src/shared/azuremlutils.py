#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from azure.ai.ml import MLClient
from azureml.core import Workspace
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential


def get_credential(useMsi=False):
    """Get Credentials to connect to Azure ML """

    # TODO: here we'd add support for conditional credentials depending on local or AzureML run

    if useMsi:
        client_id = os.environ.get('DEFAULT_IDENTITY_CLIENT_ID')
        credential = ManagedIdentityCredential(client_id=client_id)
    else:
        credential = DefaultAzureCredential()

    return credential


def get_mlclient(path, useMsi=False):
    """Get a ML Client to connect to Azure ML """

    credential = get_credential(useMsi)

    try:
        ml_client = MLClient.from_config(credential=credential, path=path)
    except Exception as ex:
        # TODO: log issue with credentials
        print(f"Failed to create MLClient - useMsi={useMsi}")
        raise Exception("Failed to create MLClient - useMsi={useMsi}") from ex

    return ml_client


def write_config_file(subscription_id, resource_group, workspace_name):

    client_config = {
        "subscription_id": f"{subscription_id}",
        "resource_group": f"{resource_group}",
        "workspace_name": f"{workspace_name}",
    }

    path = "../.azureml/config.json"

    # write config file
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fo:
            fo.write(json.dumps(client_config))
    except Exception as ex:
        # TODO: log issue with config
        print("Failed to write MLClient config file")
        raise Exception("Failed to write MLClient config file") from ex

    return path


def get_aml_client(subscription_id, resource_group, workspace_name):
    """Connect to Azure ML workspace using provided cli arguments."""

    config_path = write_config_file(subscription_id, resource_group, workspace_name)

    # Get a ML Client
    try:
        ml_client = get_mlclient(path=config_path, useMSI=True)

    except Exception as ex:
        try:
            print("Attempting to use fallback DefaultAzureCredential")
            ml_client = get_mlclient(path=config_path)

        except Exception as ex:
            # TODO: log issue with config
            print("Unable to connect to Azure ML workspace with current credentials")
            raise Exception("Unable to connect to Azure ML workspace with current credentials") from ex

    print(ml_client)
    return ml_client


def get_workspace():
    """Get a ML Client to connect to Azure ML """

    try:
        workspace = Workspace.from_config()
    except Exception as ex:
        # TODO: log issue with credentials
        print(f"Failed to create Workspace")
        raise Exception("Failed to create Workspace") from ex

    return workspace


def get_aml_workspace(subscription_id, resource_group, workspace_name):
    """Connect to Azure ML workspace using provided cli arguments."""

    config_path = write_config_file(subscription_id, resource_group, workspace_name)

    # Get a ML Client
    try:
        ws = get_workspace()

    except Exception as ex:
        try:
            print("Attempting to use fallback DefaultAzureCredential")
            ws = get_workspace()

        except Exception as ex:
            # TODO: log issue with config
            print("Unable to connect to Azure ML workspace with current credentials")
            raise Exception("Unable to connect to Azure ML workspace with current credentials") from ex

    print(ws)
    return ws
