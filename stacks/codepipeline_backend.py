from aws_cdk import (
    aws_codepipeline as cp,
    aws_codepipeline_actions as cp_actions,
    aws_codebuild as cb,
    aws_s3 as s3,
    aws_secretsmanager as sm,
    aws_iam as iam,
    aws_ssm as ssm,
    core
) 

class CodePipelineBackendStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, artifactbucket, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        artifact_bucket = s3.Bucket.from_bucket_name(self, 'artifactbucket', bucket_name=artifactbucket)
        github_token = core.SecretValue.secrets_manager(
            'dev/github-token', json_field='github-token'
        )

        #this stack depends upon the serverless application I have on GitHub. And so, the Github token is evoked.
        #I generated the token and put the value in secrets manager. The above argument calls it.

        build_project = cb.PipelineProject(self, 'build-project',
            #project_name='build-project',
            #description='Package Lambda Functions',
            #environment=cb.BuildEnvironment(
                #build_image=cb.LinuxBuildImage.STANDARD_3_0,
                #environment_variables={
                    #'ENV':cb.BuildEnvironmentVariable(value='dev'),
                    #'PRJ':cb.BuildEnvironmentVariable(value=prj_name),
                    #'STAGE':cb.BuildEnvironmentVariable(value='dev')
                #}
            #),
            #cache=cb.Cache.bucket(artifact_bucket, prefix='codebuild-cache'),
            build_spec=cb.BuildSpec.from_object({
                'version': '0.2',
                'phases': {
                    'install':{
                        'commands': [
                            'echo "--INSTALL PHASE--" ',
                            'npm install --silent --no-progress serverless -g'
                        ]
                    },
                    'pre_build':{
                        'commands':[
                            'echo "--PRE BUILD PHASE--"',
                            'npm install --silent --no-progress'
                        ]
                    },
                    'build': {
                        'commands':[
                            'echo "--BUILD PHASE--" ',
                            'serverless deploy -s $STAGE'
                        ]
                    }
                },
                'artifacts': {
                    'files': [ '**/*' ],
                    'base-directory': '.serverless'
                }    
            })
        )
        
        
        
        pipeline = cp.Pipeline(self, 'backend-pipeline',
            pipeline_name=str(env_name)+'-'+str(prj_name)+'-backend-pipeline',
            artifact_bucket=artifact_bucket,
            restart_execution_on_update=False
        )

        source_output = cp.Artifact(artifact_name=('source')), #([cp.Artifact],"source")
        build_output = cp.Artifact(artifact_name=('build')) #cp.Artifact(artifact_name="build")
        source_actions = cp_actions.GitHubSourceAction(
                action_name='GitHubSource',
                owner='ikramhm',
                repo='cdk-serverless-app',
                oauth_token=github_token,
                output=source_output,
                branch='master',                
        )

        pipeline.add_stage(stage_name="source", actions=[source_actions])

        #pipeline.add_stage(stage_name="source", actions=[
            #cp_actions.GitHubSourceAction(
                #oauth_token=github_token,
                #output=source_output,
                #repo='cdk-serverless-app',
                #branch='master',
                #owner='ikramhm',
                #action_name='GitHubSource'
            #)
        #]) #this stage just takes source code from GitHub repo to the source_output artifact bucket - ready to b build in next stage

        pipeline.add_stage(stage_name='Deploy', actions=[
            cp_actions.CodeBuildAction(
                action_name="DeploytoDev",
                input=source_output, #meaning where is it receiving things from; the source s3 bucket.
                project=build_output,
                outputs=build_output, #the artifacts at this stage will be left there.
                #if we had a third stage, build_output would become input for that stage
            )

        ])

        build_project.role.add_to_policy(iam.PolicyStatement(
            actions={'cloudformation:*', 's3:*', 'iam:*', 'lambda:*', 'apigateway:*'}
        ))

        #build_project.role.add_managed_policy(
            #iam.ManagedPolicy.from_aws_managed_policy_name('AdministratorAccess')
        #)

        account_id = core.Aws.ACCOUNT_ID
        region = core.Aws.REGION

        ssm.StringParameter(self,'accountid',
            parameter_name='/'+env_name+'/account-id',
            string_value=account_id
        )

        ssm.StringParameter(self, 'region',
            parameter_name='/'+env_name+'/region',
            string_value=region
        )