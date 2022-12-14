#see this aws link for an out-of-box CFormation stack for WAF with the most common WAF RULES set up
#https://docs.aws.amazon.com/solutions/latest/security-automations-for-aws-waf/welcome.html

from aws_cdk import (
    aws_wafv2 as waf,
    aws_iam as iam,
    aws_ssm as ssm,
    core
) 

class WafStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str,  **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        basic_rule = waf.CfnWebACL.RuleProperty(
            name='AWSManagedCommonRule',
            priority=0,
            statement= waf.CfnWebACL.StatementProperty(
                managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                    name='AWSManagedRulesCommonRuleSet',
                    vendor_name='AWS'
                )
            ),
            override_action=waf.CfnWebACL.OverrideActionProperty(count={}),
            visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name='AWSManagedCommonRule',
                sampled_requests_enabled=True
            )
        )

        web_acl = waf.CfnWebACL(self, 'web-acl-id',
            default_action=waf.CfnWebACL.DefaultActionProperty(allow={}),
            scope='CLOUDFRONT',
            visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name=prj_name+'-'+env_name,
                sampled_requests_enabled=True
            ),
            name=prj_name+'-'+env_name+'webacl',
            rules=[ basic_rule ] #this is a list, if you had multiple rules, you'd just list them here.
        )

        ssm.StringParameter(self, 'webacl-id-ssm',
            parameter_name='/'+env_name+'/webacl-id',
            string_value=web_acl.attr_id
        )