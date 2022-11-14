from aws_cdk import (
    aws_codepipeline as cp,
    aws_codepipeline_actions as cp_actions,
    aws_codecommit as ccm,
    aws_codebuild as cb,
    aws_s3 as s3,
    aws_iam as iam,
    aws_ssm as ssm,
    core
) 

class CodePipelineFrontendStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, webhostingbucket, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        webhosting_bucket = s3.Bucket.from_bucket_name(self, 'webhosting-id', bucket_name=webhostingbucket)
        #this has been repeated elsewhere. You are ref an existing bucket; imported already in the constructer(i.e, webhostingbucket), which is then defined in the app.py
        #same thing is taking place below - you are calling upon a param or repo, you do same thing.
        cdn_id = ssm.StringListParameter.from_string_list_parameter_name(self, 'cdn-id', string_list_parameter_name='/'+env_name+'/app-distribution-id')
        source_repo = ccm.Repository.from_repository_name(self, 'repo-id', repository_name='devops')
        #these values are not imported in constructer because they are being hardcoded/ref directly!

        artifact_bucket = s3.Bucket(self, 'artifact',
            encryption=s3.BucketEncryption.S3_MANAGED,
            access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL
        ) 

        build_project = cb.PipelineProject(self, 'buildfrontend',
            project_name='BuildFrontend',
            description='front-end build for single page application',
            environment=cb.BuildEnvironment(
                build_image= cb.LinuxBuildImage.STANDARD_3_0,
                environment_variables={'distributionid': cb.BuildEnvironmentVariable(value=cdn_id.string_list_value)},
                #this variable is passing the CFront distribution id to the build stage as a post-install command to invalidate
            ),
            cache=cb.Cache.bucket(bucket=artifact_bucket, prefix='codebuild-cache'),
            build_spec=cb.BuildSpec.from_object({
                'version': '0.2',
                'phases':{
                    'install': {
                        'commands': [
                            'pip install awscli'
                        ]
                    },
                    'pre_build': {
                        'commands': [
                            'yarn install'
                        ]
                    },
                    'build': {
                        'commands': [
                            'yarn run build'
                        ]
                    },
                    'post_build':{
                        'commands':[
                            'aws cloudfront create-invalidation --distribution-id $distributionid --paths "/*" '
                        ]
                    }
                },
                'artifacts': {
                    'files': [
                        'build/**/*'
                    ]
                },
                'cache': {
                    'paths': [ './node_modules/**/*']
                }
            })
        )

        pipeline = cp.Pipeline(self, 'frontend-pipeline',
            pipeline_name=prj_name+'-'+env_name+'-frontend-pipeline',
            artifact_bucket=artifact_bucket,
            restart_execution_on_update=False
        )

        #These are artifact definitions: you define them here so they can be referrenced for cb.
        source_output= cp.Artifact(artifact_name='source'),
        build_output= cp.Artifact(artifact_name='build')

        pipeline.add_stage(stage_name='Source', actions=[
            cp_actions.CodeBuildAction(
                action_name='CodeCommitSource',
                repository=source_repo,
                outputs=source_output
            )
        ])
        
        pipeline.add_stage(stage_name='Build', actions=[
            cp_actions.CodeBuildAction(
                action_name='Build',
                input=source_output,
                project=build_project, #thsi refs the CodeBuild stage and buildspec etc
                outputs=[build_output]
            )
        ])

        pipeline.add_stage(stage_name='Deploy', actions=[
            cp_actions.S3DeployAction(
                bucket=webhosting_bucket,
                input=build_output,
                action_name='Deploy',
                extract=True
            )
        ])
        ##learn these in some detail - creating pipelines is an essential DevOps task.
        #https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_codepipeline_actions.html
        
        build_project.role.add_to_policy(iam.PolicyStatement(actions=['cloudfront:CreateInvalidation'], resources=['*']))