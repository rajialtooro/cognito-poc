import React from "react";
import ReactDOM from "react-dom";
import "./index.css";
import App from "./App";
import reportWebVitals from "./reportWebVitals";
import Amplify, { Auth } from "aws-amplify";
Amplify.configure({
  Auth: {
    region: "eu-central-1",
    userPoolId: "eu-central-1_4R0OY2MHG",
    userPoolWebClientId: "70su5u8ctonipbcjdkggghgqim",
    oauth: {
      domain: "auth.development.altooro.com",
      scope: ["openid"],
      redirectSignIn: "http://localhost:3000/",
      redirectSignOut: "http://localhost:3000/",
      responseType: "code",
    },
  },
});

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById("root")
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
