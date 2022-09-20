import aws_cdk as core
import aws_cdk.assertions as assertions

from webserver.webserver_stack import WebserverStack

# example tests. To run these tests, uncomment this file along with the example
# resource in webserver/webserver_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = WebserverStack(app, "webserver")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
