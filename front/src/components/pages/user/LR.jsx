import React, {useEffect, useState} from 'react';
import './LR.css'

import { serverUrl } from '../../Config.jsx'

import BG1 from '../../../imgs/bg.png'
import BG2 from '../../../imgs/bg2.png'
import BG3 from '../../../imgs/bg3.png'
import '../../../imgs/bg4.png'

import axios from "axios";
import {getCsrfToken} from "../../../CSRF.jsx";
import Request from "./Request.jsx";
import Enter from "./Enter.jsx";

import { useNavigate } from "react-router-dom";





function LR() {
    const navigate = useNavigate();

    const [csrf, setCsrfToken] = useState(null)
    const [isRequest, setIsRequest] = useState(null)
    const [isEnter, setIsEnter] = useState(null)

    const handleSuccess = () => {
        setIsRequest(prev => !prev);
    };
    const handleEnter = () => {
        setIsEnter(prev => !prev);
    };


    useEffect(() => {
        getSession()
    }, [])

    // useEffect(() => {
    //     console.log(userId, isAuth, username)
    // }, [userId, isAuth, username]);


    useEffect(() => {
        if (isEnter === true) {
            navigate("/");
        }
    }, [isEnter, navigate]);


    const getSession = () => {
        axios.get(serverUrl + "api/is-auth/", { withCredentials: true })
            .then((res) => {
                if (res.data.is_auth) {
                    navigate('/')
                } else {
                    getCsrfToken().then(token => {
                        setCsrfToken(token)
                    });
                }
            })
            .catch(() => console.error)
    }

    // const userInfo = () => {
    //     axios.get(serverUrl + "api/user_info/", {
    //         withCredentials: true,
    //         headers: {"Content-Type": "application/json",},
    //     })
    //         .then((res) => {
    //             console.log("Вы авторизованы как: " + res.data.username);
    //             setUsername(res.data.username)
    //         })
    //         .catch((err) => {
    //             if (err.status === 401) console.log(err.error);
    //         });
    // }

    return (
        <>
            {!isRequest ? (
                <Request
                    csrf={csrf}
                    handleSuccess={handleSuccess}
                />
            ) : (
                <Enter
                    csrf={csrf}
                    handleEnter={handleEnter}
                />
            )}
        </>
    )
}

export default LR;