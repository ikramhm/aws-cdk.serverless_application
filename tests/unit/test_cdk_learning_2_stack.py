import json
import pytest

from aws_cdk import core
from cdk-learning-2.cdk_learning_2_stack import CdkLearning2Stack


def get_template():
    app = core.App()
    CdkLearning2Stack(app, "cdk-learning-2")
    return json.dumps(app.synth().get_stack("cdk-learning-2").template)


def test_sqs_queue_created():
    assert("AWS::SQS::Queue" in get_template())


def test_sns_topic_created():
    assert("AWS::SNS::Topic" in get_template())
