from aws_cdk import (
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_ssm as ssm,
    core
)

class SecurityStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str,vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        self.lambda_sg = ec2.SecurityGroup(self, 'lambda_sg',
            security_group_name='lambda-sg',
            vpc=vpc,
            description='SG for Lambda Functions',
            allow_all_outbound=True,    
        )

        self.bastion_sg = ec2.SecurityGroup(self, 'bastion_sg',
            security_group_name="bastion-sg",
            vpc=vpc,
            description="SG for Bastion Host Ec2",
            allow_all_outbound=True,
        )

        #adding ingress and egress ruls as follows
        self.bastion_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "SSH Access")

        redis_sg = ec2.SecurityGroup(self, 'redis_sg',
            security_group_name='redis-sg',
            vpc=vpc,
            description='SG for Redis Cluster',
            allow_all_outbound=True,    
        )

        redis_sg.add_ingress_rule(self.lambda_sg, ec2.Port.tcp(6379),'Access from Lambda Function')
        #important note on sg - ((ips_you're_allowing), (ports) (description))
        
        
        lambda_role = iam.Role(self, "Lambda-role",
            assumed_by=iam.ServicePrincipal(service='lambda.amazon.aws/com'),
            role_name="lambda-role",
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name(
                managed_policy_name='service-role/AWSLambdaVPCAccessExecutionRole'
            )]
        )

        #creating an Inline policy for that lambda role to give further permissions to s3 and RDS    
        lambda_role.add_to_policy(
            statement=iam.PolicyStatement(
                actions=['s3:*', 'rds:*'],
                resources=['*']
            )
        ) 

        core.CfnOutput(self, 'redis-export',
            export_name='redis-sg-export',
            value=redis_sg.security_group_id
        #critical matter here. EC is not fully developped on CDK; its an unstable release and so it does not suppor exporting through self.
        #this is why you have to use API calls to CFormation directly; so create a Cfn output to export something from redis.
        #this is then declared appropriately in app.py using the Fn - as if you would do Ref! in CloudFormation
        )


        #sg-setup-for-kibana
        self.kibana_sg = ec2.SecurityGroup(self, 'kibanasg',
            security_group_name='kibana-sg',
            vpc=vpc,
            description='SG for Kibana',
            allow_all_outbound=True,     
        )

        self.kibana_sg.add_ingress_rule(self.bastion_sg, ec2.Port.tcp(443), 'Access from bastion-host')

        kibana_role= iam.CfnServiceLinkedRole(self, 'kibanarole',
            aws_service_name="es.amazonaws.com"
        )


        #Stored Values for SSM Paramter Store    
        ssm.StringParameter(self, 'lambdasg-param',
            parameter_name='/'+env_name+'/lambda-sg',
            string_value=self.lambda_sg.security_group_id
        )

        ssm.StringParameter(self, 'lambdarole-param-arn',
            parameter_name='/'+env_name+'/lambda-role-arn',
            string_value=lambda_role.role_arn
        )
        ssm.StringParameter(self, 'lambdarole-param-name',
            parameter_name='/'+env_name+'/lambda-role-name',
            string_value=lambda_role.role_name
        )

        