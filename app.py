#!/usr/bin/env python3

from aws_cdk import core
from cdk_learning_2.cdk_learning_2_stack import CdkLearning2Stack
from stacks.vpc_stack import VPCStack
from stacks.security_stack import SecurityStack
from stacks.bastion_stack import BastionStack
from stacks.kms_stack import KMSStack
from stacks.s3_stacks import S3Stack
from stacks.rds_stack import RDSStack
from stacks.redis_stack import RedisStack
from stacks.cognito_stack import CognitoStack
from stacks.apigw_stack import APIStack
from stacks.lambda_stack import LambdaStack
from stacks.codepipeline_backend import CodePipelineBackendStack
from stacks.notifications_stack import NotificationStack
from stacks.cdn_stack import CDNStack
from stacks.codepipeline_frontend import CodePipelineFrontendStack
from stacks.waf_stack import WafStack
from stacks.route53_stack import DnsStack
from stacks.acm_stack import ACMStack
from stacks.cloudtrail_stack import CloudTrailStack
from stacks.kibana_stack import KibanaStack


app = core.App()

CdkLearning2Stack(app, "cdk-learning-2", env={'region': 'us-west-2'})
vpc_stack = VPCStack (app, 'vpc')
security_stack = SecurityStack (app, 'security-stack', vpc=vpc_stack.vpc)
bastion_stack = BastionStack (app, 'bastion', vpc=vpc_stack.vpc, sg=security_stack.bastion_sg)
kms_stack = KMSStack (app, 'kms-stack')


s3_stack = S3Stack (app, 's3-buckets')
rds_stack = RDSStack (app, 'rds-stack', vpc=vpc_stack.vpc, lambdasg=security_stack.lambda_sg, bastionsg=security_stack.bastion_sg, kmskey=kms_stack.kms_rds)
redis_stack= RedisStack (app, 'redis-stack', vpc=vpc_stack.vpc, redissg=core.Fn.import_value('redis-sg-export'))

cognito_stack= CognitoStack (app, 'cognito-stack')
apigw_stack= APIStack (app, 'api-gw')
lambda_stack= LambdaStack (app, 'lambda')

codepipeline_backend = CodePipelineBackendStack (app, 'cp-backend', artifactbucket=core.Fn.import_value('build-artifacts-bucket'))
notification_stack = NotificationStack(app, 'notification')
codepipeline_frontend = CodePipelineFrontendStack (app, 'cp-frontend', webhostingbucket=core.Fn.import_value('frontend-bucket'))
waf_stack = WafStack (app, 'waf')


acm_stack = ACMStack (app, 'acm')
cdn_stack = CDNStack (app, 'cdn', s3Bucket=core.Fn.import_value('frontend-bucket'), acmcert=acm_stack.cert_manager)
route53_stack = DnsStack (app,'route53', cdnid=cdn_stack.cdn_id)

cloudtrail_stack = CloudTrailStack (app, 'cloudtrail', s3bucket=s3_stack.cloudtrail_bucket)
kibana_stack = KibanaStack (app, 'kibana', vpc=vpc_stack.vpc, kibanasg=security_stack.kibana_sg)

app.synth()

#syntax is (app, "local name you will give to the CF stack"
#as mentioned in some of the stack files, if a stack constructer definition calls upon a parent stack
#eg "vpc: ec2.Vpc", the path is declared here. so vpc=(stack-file-name).(imported-value) so vpc=vpc_stack.vpc
#if you are calling upon a certain stack, but its not being instantiated above, check that you have allowed the value to be exported.
#meaning self.cdn_id, self,vpc_id etc. or the core.CfOutput method. method.