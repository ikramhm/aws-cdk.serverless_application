from aws_cdk import (
    aws_route53 as r53,
    aws_route53_targets as r53target,
    aws_iam as iam,
    aws_cloudfront as cdn,
    aws_ssm as ssm,
    core
) 

class DnsStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str,cdnid,  **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        hosted_zone = r53.HostedZone(self, 'hosted-zone', zone_name='zone-name.com'),
        
        #hosted_zone_1 = r53.HostedZone.from_lookup(self, 'hosted-zone-id', domain_name=whatever)
        #template for setting a record is as so: r53.ARecord(self, 'dev', zone=hosted_zone, target=r53.RecordTarget.from_ip_addresses('1.1.1.1'), record_name='dev')

        r53.ARecord (self, 'cdn-record', 
        zone=hosted_zone, 
        target=r53.RecordTarget.from_alias(alias_target=r53target.CloudFrontTarget(cdnid)),
         record_name='app'
        )
        #https://docs.aws.amazon.com/cdk/api/v1/docs/aws-route53-targets-readme.html

        ssm.StringParameter(self, 'zone-id',
            parameter_name='/'+env_name+'/zone-id',
            string_value=hosted_zone.hosted_zone_id
        )