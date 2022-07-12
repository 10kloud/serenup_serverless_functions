import boto3

from mypy_boto3_cognito_idp.client import CognitoIdentityProviderClient


class CognitoIDPUserPool:
    def __init__(self, user_pool_id: str):
        self.__client: CognitoIdentityProviderClient = boto3.client('cognito-idp')
        self.__user_pool_id = user_pool_id

    def filter_user_by_sub(self, sub: str):
        response = self.__client.list_users(
            UserPoolId=self.__user_pool_id,
            Filter=f'sub = "{sub}"'
        )
        return response

