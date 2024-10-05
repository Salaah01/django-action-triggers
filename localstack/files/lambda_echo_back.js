exports.handler = async (event) => {
  return {
    statusCode: 200,
    title: 'Echo Back Lambda Function',
    body: event,
  };
};
