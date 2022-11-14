from aws_cdk import (
    aws_ec2 as ec2,
    aws_ssm as ssm,
    core
)

class BastionStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str,vpc: ec2.Vpc, sg: ec2.SecurityGroup, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

    #most of this is just copy and paste; the only thing you will add are refs to these PARENT STACKS (neccesary dependent resources declared elsewhere, like the vpc, or the sg).
    #these will also need to be declared in the app.py as: sg=ec2.SecurityGroup.whatever, and vpc=vpc.Vpc.whatever, to ref them.
        bastion_host = ec2.Instance(self, 'bastion',
            instance_type= ec2.InstanceType("t2.micro"),
            machine_image=ec2.AmazonLinuxImage(
                edition=ec2.AmazonLinuxEdition.STANDARD,
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
                virtualization=ec2.AmazonLinuxVirt.HVM,
                storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
                ),
                vpc=vpc, #you have declared this in the initiataing the class and app.py; therefore, its simple.
                key_name='devops',
                vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC,   
                ),
                security_group=sg
            )

