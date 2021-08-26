const aws = require("aws-sdk");

const cognito = new aws.CognitoIdentityServiceProvider({
  region: "eu-central-1",
  accessKeyId: ``,
  secretAccessKey: ``,
  sessionToken: ``,
});
const cognito2 = new aws.CognitoIdentityServiceProvider({
  region: "eu-central-1",
  accessKeyId: ``,
  secretAccessKey: ``,
  sessionToken: ``,
});
const getUsers = (token) => {
  cognito.listUsers({ UserPoolId: ``, PaginationToken: token }, (err, data) => {
    if (err) {
      throw err;
    }
    if (data.Users) {
      data.Users.forEach((user) => {
        if (user.UserStatus == "CONFIRMED" && user.Enabled) {
          cognito2.adminCreateUser({
            UserPoolId: ``,
            Username: user.Username,
            UserAttributes: user.Attributes,
            ClientMetadata,
          });
        }
      });
      if (data.PaginationToken) {
        getUsers(data.PaginationToken);
      }
    }
  });
};

getUsers();
