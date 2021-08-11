import React, { useEffect } from "react";
import { getIdToken, getSession, signIn } from "./cognito";

const authPage = () => {
  useEffect(() => {
    getSession().then(console.log).catch(console.log);
  }, []);
  return (
    <div>
      <button
        onClick={() => {
          signIn("username", "password").then(console.log).catch(console.log);
        }}
      >
        login
      </button>
      <button
        onClick={() => {
          getIdToken().then(console.log).catch(console.log);
        }}
      >
        token
      </button>
      <button
        onClick={async () => {
          fetch("https://api.development.altooro.com", {
            headers: {
              Authorization: await getIdToken(),
            },
          })
            .then((data) => data.text())
            .then(console.log)
            .catch(console.log);
        }}
      >
        fetch
      </button>
    </div>
  );
};

export default authPage;
