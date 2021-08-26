import React from "react";
import ReactDOM from "react-dom";
import "./index.css";
import App from "./App";
import { configure } from "./cognito";
import * as AmazonCognitoIdentity from "amazon-cognito-identity-js";

configure({
  ClientId: "68lpd255gkpsmfb97jfh00c6e7",
  UserPoolId: "eu-central-1_4R0OY2MHG",
  Storage: new AmazonCognitoIdentity.CookieStorage({
    domain: "localhost",
  }),
});

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById("root")
);
