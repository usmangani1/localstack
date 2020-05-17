import unittest
from localstack.utils.aws import aws_stack


class TestSESIntegrations(unittest.TestCase):
    def setUp(self):
        self.ses_client = aws_stack.connect_to_service('ses')

    def test_create_configuration_set(self):
        conn = self.ses_client
        conn.create_configuration_set(ConfigurationSet=dict({'Name': 'test'}))

        conn.create_configuration_set_event_destination(
            ConfigurationSetName='test',
            EventDestination={
                'Name': 'snsEvent',
                'Enabled': True,
                'MatchingEventTypes': ['send'],
                'SNSDestination': {
                    'TopicARN': 'arn:aws:sns:us-east-1:123456789012:myTopic'
                },
            },
        )

        self.assertRaises(Exception, conn.create_configuration_set_event_destination,
            ConfigurationSetName='failtest',
            EventDestination={
                'Name': 'snsEvent',
                'Enabled': True,
                'MatchingEventTypes': ['send'],
                'SNSDestination': {
                    'TopicARN': 'arn:aws:sns:us-east-1:123456789012:myTopic'
                },
            }
        )

        self.assertRaises(Exception, conn.create_configuration_set_event_destination,
            ConfigurationSetName='test',
            EventDestination={
                'Name': 'snsEvent',
                'Enabled': True,
                'MatchingEventTypes': ['send'],
                'SNSDestination': {
                    'TopicARN': 'arn:aws:sns:us-east-1:123456789012:myTopic'
                },
            },
        )

    def test_get_send_statistics(self):
        conn = self.ses_client
        # tests to verify rejects in get_send_statistics
        email_address = 'test@example.com'
        conn.verify_email_identity(EmailAddress=email_address)

        conn.send_email(
            Source=email_address,
            Destination={'ToAddresses': ['your.friend@hotmail.com']},
            Message={'Subject': {'Data': 'hi', }, 'Body': {'Text': {'Data': 'there', }}},
        )

        # tests to delivery attempts in get_send_statistics
        result = conn.get_send_statistics()

        delivery_count = int(
            result['GetSendStatisticsResponse']['SendDataPoints'][0]['DeliveryAttempts']
        )

        self.assertEqual(delivery_count, 1)
