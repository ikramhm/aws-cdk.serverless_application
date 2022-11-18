
# Challenging! My Story from Beginner Python-er to Intermediate

This application is the amalgamation of an outdatted Udemy course and lots of research. Whiel I will not name the course or it's instructor, unfortunately, much of the code presented in the videos did not work. AWS had introduced new variablenames or an entire new version of the Python CDK, and so, each individual unit involved much research through github! The course taught some of the fundamentals; in places where the video instruction did not work, I referred to either the official AWS documenation (https://docs.aws.amazon.com/cdk/api/v1/python/index.html) or the following github repo (https://github.com/aws-samples/aws-cdk-examples/tree/master/python). Thankfully, the documentation was easy to follow! The course was 7 hours long - It took me 2 months to complete this course! Its lucky that RESEARCH is my day-job!


<p align="center">
  <img width="700" height="300" src="https://user-images.githubusercontent.com/98710900/202811333-275be33a-f183-469d-a86c-df0e561e2a5f.png">
</p>

The architecture of the project is as follows. The entire architecture is built together through individiual configuration stacks per service. All the stacks are fully functioning, with the exception of (codepipeline_backened, codepipeline_frontend). The client will access the app through Route53, which will route them to a CloudFront distribution. Static content will be served through an S3, while dynamic content (API work) will be staged through an API Gateway-Lambda-RDSAurora intregration. There are various other features: VPCs, WAF & Shield intergration, alongside monitoring through CloudWatch, CloudTrail and ElasticSearch (kibana can be installed therein).


Why did I start this? I had just passed the AWS Developer Associate exam and was focussing on learning Python. I had gained some begginner Python proficiencies, creating a few "powerful" python scripts. I had no real developping experience though! My mentor thought that learning the CDK for Python might help allign my learning! This experience with OOP and Constucts has elevated my Python knowledge. By no means am I a comfortable python programmer, but this experience with python data and syntax fundamentals + AWS documentation + github + google search, has equalled immense depth in knowledge.

Since this project, I have since moved on to learning Terraform which has been a revelation! More on that later!


<h><h/>
<h><h/>
<h><h/>
<h><h/>
<h><h/>
<h><h/>
<h><h/>
<h><h/>
<h><h/>
<h><h/>
<h><h/>
<h><h/>
<h><h/>
<h><h/>
<h><h/>
<h><h/>
<h><h/>
<h><h/>
   


























# Welcome to your CDK Python project!

You should explore the contents of this project. It demonstrates a CDK app with an instance of a stack (`cdk_learning_2_stack`)
which contains an Amazon SQS queue that is subscribed to an Amazon SNS topic.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization process also creates
a virtualenv within this project, stored under the .env directory.  To create the virtualenv
it assumes that there is a `python3` executable in your path with access to the `venv` package.
If for any reason the automatic creation of the virtualenv fails, you can create the virtualenv
manually once the init process completes.

To manually create a virtualenv on MacOS and Linux:

```
$ python -m venv .env
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .env/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .env\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

You can now begin exploring the source code, contained in the hello directory.
There is also a very trivial test included that can be run like this:

```
$ pytest
```

To add additional dependencies, for example other CDK libraries, just add to
your requirements.txt file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
