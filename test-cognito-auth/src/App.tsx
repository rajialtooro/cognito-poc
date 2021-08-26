import React, { useEffect } from "react";
import {
  getIdToken,
  getSession,
  getValidSessionUser,
  signIn,
  updateUserAttributes,
} from "./cognito";

const authPage = () => {
  useEffect(() => {
    getSession().then(console.log).catch(console.log);
  }, []);
  return (
    <div>
      <button
        onClick={() => {
          signIn("rajihawa", "Raji123Hawa!")
            .then(console.log)
            .catch(console.log);
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
        onClick={() => {
          updateUserAttributes({ address: "INDIVIDUAL" })
            .then(console.log)
            .catch(console.log);
        }}
      >
        make individual
      </button>
      <button
        onClick={async () => {
          fetch("https://journeys.development.altooro.com/journey/543632", {
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
