import {Link} from "react-router-dom";
import {useEffect, useState} from "react";
import axios from "axios";
import {serverUrl} from "../../Config.jsx";

function Logout() {
    const [detail, setMessage] = useState("");

    useEffect(() => {
        axios.get(`${serverUrl}api/logout/`, {withCredentials: true})
            .then((res) => {
                setMessage(res.data.detail)
            })
            .catch((err) => {
                setMessage("Ошибка повторите позже")
            })
    }, [])

    return (
        <div className="main-block logout" style={{ alignSelf: 'center', justifySelf: 'center', width: 'max-content', height: 'max-content', display: "grid", placeContent: "center", gap: '1rem', color: "var(--txt-color)" }}>

            {detail && (
                <h2 style={{ textAlign: 'center' }}>{detail}</h2>
            )}

            <div style={{ display: "flex", gap: '1rem', justifyContent: "space-between", textDecoration: "underline" }}>
                <Link to="/">На главную</Link>
                <Link to="/user/lr">Вход</Link>
            </div>
        </div>
    );
}

export default Logout;