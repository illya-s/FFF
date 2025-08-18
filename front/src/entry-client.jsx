import React from "react";
import { hydrateRoot } from "react-dom/client";
import Legal from "./components/pages/support/Legal.jsx";

hydrateRoot(
    document.getElementById("root"),
    <Legal initialLegal={window.__INITIAL_DATA__} />
);
