const AWS = require('aws-sdk');

const QUEUE_NAME = 'echo-back-queue';

const sqs = new AWS.SQS({ apiVersion: '2012-11-05' });

const getQueueUrl = async (queueName) => {
  const result = await sqs.getQueueUrl({ QueueName: queueName }).promise();
  return result.QueueUrl;
}

exports.handler = async (event) => {
  console.log("Received event:", JSON.stringify(event, null, 2));

  const queueUrl = getQueueUrl(QUEUE_NAME);
  const params = {
    QueueUrl: queueUrl,
    MessageBody: JSON.stringify(event),
  };

  try {
    const result = await sqs.sendMessage(params).promise();
    console.log("Message sent to SQS:", result.MessageId);

    return {
      statusCode: 200,
      body: JSON.stringify({
        message: "Event forwarded to SQS",
        messageId: result.MessageId
      }),
    };
  } catch (error) {
    console.error("Error sending message to SQS:", error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        message: "Failed to send message to SQS",
        error: error.message
      }),
    };
  }
};
