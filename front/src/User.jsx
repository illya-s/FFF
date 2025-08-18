import React, { useState, useEffect } from "react";
import axios from "axios";
import { serverUrl } from "./components/Config.jsx";

import { UserContext } from "./UserContext.jsx";


export function UserProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        axios.get(serverUrl + "api/session/", { withCredentials: true })
            .then(res => {
                if (res.data.isAuthenticated) {
                    setUser({
                        id: res.data.id,
                        username: res.data.username,
                        email: res.data.email,
                        avatar: res.data.avatar,
                        joined: res.data.joined,
                        session: res.data.session,
                    });
                } else {
                    setUser(null);
                }
            })
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    return (
        <UserContext.Provider value={{ user, loading }}>
            {children}
        </UserContext.Provider>
    );
}
