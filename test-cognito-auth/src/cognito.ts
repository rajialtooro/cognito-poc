//@ts-nocheck
// import * as AmazonCognitoIdentity from "amazon-cognito-identity-js";
//@ts-ignore
import * as AmazonCognitoIdentity from "amazon-cognito-identity-js/dist/amazon-cognito-identity";

let userPool: AmazonCognitoIdentity.CognitoUserPool;

export function configure(
  poolConfig: AmazonCognitoIdentity.ICognitoUserPoolData
) {
  userPool = new AmazonCognitoIdentity.CognitoUserPool(poolConfig);
}

function checkPool() {
  if (!userPool) throw new Error("Cognito User Pool has not been configured");
}

export async function updateUserAttributes(
  attributes: Record<string, string>
): Promise<string | undefined> {
  return new Promise((resolve, reject) => {
    const currentUser = userPool.getCurrentUser();
    if (!currentUser) return reject("not signed in");
    currentUser.updateAttributes(
      Object.entries(attributes).map(
        ([k, v]) =>
          new AmazonCognitoIdentity.CognitoUserAttribute({ Name: k, Value: v })
      ),
      function (err, result) {
        if (err) {
          reject(err.message || JSON.stringify(err));
          return;
        }
        resolve(result);
      }
    );
  });
}

export async function getSession(): Promise<AmazonCognitoIdentity.CognitoUserSession> {
  checkPool();
  return new Promise((resolve, reject) => {
    const currentUser = userPool.getCurrentUser();
    if (!currentUser) return reject("not signed in");
    currentUser.getSession(
      (err: unknown, session: AmazonCognitoIdentity.CognitoUserSession) => {
        if (err) return reject(err);
        if (!session) return reject("no user data");
        resolve(session);
      }
    );
  });
}

export async function getValidSessionUser(): Promise<AmazonCognitoIdentity.CognitoUser> {
  checkPool();
  return new Promise((resolve, reject) => {
    const currentUser = userPool.getCurrentUser();
    if (!currentUser) return reject("not signed in");
    currentUser.getSession(
      (err: unknown, session: AmazonCognitoIdentity.CognitoUserSession) => {
        if (err) return reject(err);
        if (!session) return reject("no session");
        if (!session.isValid) return reject("session invalid");
        resolve(currentUser);
      }
    );
  });
}

export async function getUserData(): Promise<AmazonCognitoIdentity.UserData> {
  checkPool();
  const currentUser = await getValidSessionUser();
  return new Promise((resolve, reject) => {
    currentUser.getUserData((err, userData) => {
      if (err) return reject(err);
      if (!userData) return reject("no user data");
      resolve(userData);
    });
  });
}

export async function getUserAttributes(): Promise<Record<string, string>> {
  checkPool();
  const currentUser = await getValidSessionUser();
  return new Promise((resolve, reject) => {
    currentUser.getUserAttributes((err, userAttributes) => {
      if (err) return reject(err);
      if (!userAttributes) return reject("no user data");
      resolve(
        userAttributes.reduce(
          (acc: Record<string, string>, attribute) => ({
            ...acc,
            [attribute.Name]: attribute.Value,
          }),
          {}
        )
      );
    });
  });
}

export async function getIdToken() {
  checkPool();
  const session = await getSession();
  if (!session.isValid) throw new Error("invalid session");
  return session.getIdToken().getJwtToken();
}

function getCookie(cname: string) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(";");
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == " ") {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

export function signIn(username: string, password: string) {
  checkPool();
  return new Promise((resolve, reject) => {
    const authenticationDetails =
      new AmazonCognitoIdentity.AuthenticationDetails({
        Username: username,
        Password: password,
      });
    const cognitoUser = new AmazonCognitoIdentity.CognitoUser({
      Username: username,
      Pool: userPool,
      Storage: new AmazonCognitoIdentity.CookieStorage({
        domain: "localhost",
      }),
    });
    cognitoUser.authenticateUser(authenticationDetails, {
      onSuccess: (result) => resolve(result),
      onFailure: (error) => reject(error),
      // newPasswordRequired: () => reject(new Error('not implemented: new password required')),
      newPasswordRequired: () => {
        cognitoUser.completeNewPasswordChallenge(
          password,
          {},
          { onSuccess: resolve, onFailure: reject }
        );
      },
      mfaRequired: () => reject(new Error("not implemented: mfa required")),
      totpRequired: () => reject(new Error("not implemented: totp required")),
      customChallenge: () =>
        reject(new Error("not implemented: custom challenge")),
      mfaSetup: () => reject(new Error("not implemented: mfa setup")),
      selectMFAType: () =>
        reject(new Error("not implemented: select mfa type")),
    });
  });
}

export function forgotPassword(username: string) {
  checkPool();
  return new Promise((resolve, reject) => {
    const cognitoUser = new AmazonCognitoIdentity.CognitoUser({
      Username: username,
      Pool: userPool,
    });
    cognitoUser.forgotPassword({
      onSuccess: (result) => resolve(result),
      onFailure: (error) => reject(error),
    });
  });
}

export function confirmPassword(
  username: string,
  verificationCode: string,
  newPassword: string
) {
  checkPool();
  return new Promise((resolve, reject) => {
    const cognitoUser = new AmazonCognitoIdentity.CognitoUser({
      Username: username,
      Pool: userPool,
    });
    cognitoUser.confirmPassword(verificationCode, newPassword, {
      onSuccess: () => resolve(null),
      onFailure: (error) => reject(error),
    });
  });
}

export function signOut() {
  checkPool();
  const currentUser = userPool.getCurrentUser();
  if (currentUser) {
    currentUser.signOut();
  }
}
