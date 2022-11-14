from aws_cdk import (
    aws_s3 as s3,
    aws_ssm as ssm,
    core
) 

class S3Stack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        account_id = core.Aws.ACCOUNT_ID

        #Bucket for Lambda code
        lambda_bucket = s3.Bucket(self, 'lambda-bucket',
            access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            bucket_name=account_id+'-'+env_name+'-lambda-deploy-packages',
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=True,
                ignore_public_acls=True,
                restrict_public_buckets=True
            ),
            removal_policy=core.RemovalPolicy.RETAIN
        )

        ssm.StringParameter(self, 'ssm-lambda-bucker',
            parameter_name='/'+env_name+'/lambda-s3bucket',
            string_value=lambda_bucket.bucket_name
        )

        #S3 bucket to store CICD artifacts
        artifacts_bucket = s3.Bucket(self, 'artifacts-bucket',
            access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            bucket_name=account_id+'-'+env_name+'-build-artifacts',
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=True,
                ignore_public_acls=True,
                restrict_public_buckets=True
            ),
            removal_policy=core.RemovalPolicy.RETAIN
        )

        core.CfnOutput(self,'s3-build-artifacts-export',
            value=artifacts_bucket.bucket_name,
            export_name='build-artifacts-bucket'
        )

        #S3 Bucket for frontend static-hosting
        frontend_bucket=s3.Bucket(self, "frontend",
            access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            bucket_name=account_id+'-'+env_name+'-frontend',
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=True,
                ignore_public_acls=True,
                restrict_public_buckets=True
            )
        )

        #S3 Bucket for CloudTrail
        self.cloudtrail_bucket=s3.Bucket(self, "cloudtrail",
            access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            bucket_name=account_id+'-'+env_name+'-cloudtrail',
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=True,
                ignore_public_acls=True,
                restrict_public_buckets=True
            )
        )

        core.CfnOutput(self,'s3-frontend-export',
            value=frontend_bucket.bucket_name,
            export_name='frontend-bucket'
        )