import React from "react";
import { withAuthenticator, AmplifySignOut } from "@aws-amplify/ui-react";

const App = () => (
  <div>
    <AmplifySignOut />
    My App
    <button
      onClick={() => {
        fetch("https://journeys.development.altooro.com/health", {
          mode: "no-cors",
          credentials: "include",
        })
          .then(console.log)
          .catch(console.log);
      }}
    >
      fetch
    </button>
  </div>
);

export default withAuthenticator(App);
