import './Profile.css'

import {Avatar, Button, Form, Input, List, message} from "antd";
import {useContext, useEffect, useState} from "react";
import {UserContext} from "../../../UserContext.jsx";
import {User} from "../../../icons/icons.jsx";
import {serverUrl} from "../../Config.jsx";
import {Link, Navigate, useNavigate} from "react-router-dom";
import axios from "axios";
import {LoadingOutlined} from "@ant-design/icons";
import {getCsrfToken} from "../../../CSRF.jsx";

const avatarSize = { xs: 24, sm: 32, md: 40, lg: 140, xl: 120, xxl: 120 }

function Profile() {
    const navigate = useNavigate();
    const { user, loading } = useContext(UserContext);
    const [sessionLoading, setSessionLoading] = useState(true);
    const [sessionList, setSessionList] = useState([]);
    const [form] = Form.useForm();
    const [csrf, setCsrfToken] = useState(null)

    const [blockSessionLoading, setBlockSessionLoading] = useState(false);
    const [endSessionLoading, setEndSessionLoading] = useState(false);
    const [killAllSessions, setKillAllSessions] = useState(false);

    if (!user && !loading) {
        return navigate('/user/lr')
    }

    const getSessionList = () => {
        axios.get(`${serverUrl}api/session/list/`, {withCredentials: true})
            .then((response) => {
                setSessionList(response.data.list);
            })
            .catch(() => console.error)
            .finally(() => setSessionLoading(false));
    }

    const handleBlockSession = (session_key) => {
        console.log(session_key)
        setBlockSessionLoading(true);
        // axios.delete(`${serverUrl}api/session/kill/${value}/`, {withCredentials: true})
        //     .then((response) => {
        //
        //     })
        //     .catch(() => console.error)
        //     .finally(() => setEndSessionLoading(false));
    }
    const handleEndSession = (session_key) => {
        setEndSessionLoading(true);
        axios.delete(`${serverUrl}api/session/kill/${session_key}/`, {
            withCredentials: true,
            headers: {'Content-Type': 'multipart/form-data', 'X-CSRFToken': csrf}
        })
            .then((response) => {
                if (response.data.success) {
                    message.success(response.data.message)
                    setSessionList(prev =>
                        prev.filter(session => session.session_key !== session_key)
                    );
                } else {
                    message.error(response.data.message)
                }
            })
            .catch(() => console.error)
            .finally(() => setEndSessionLoading(false));
    }

    const handleKillAllSessions = () => {
        axios.delete(`${serverUrl}api/session/kill/all`)
            .then((response) => {
                if (response.data.success) {
                    message.success(response.data.message)
                    setSessionList(prev =>
                        prev[0]
                    );
                }
            })
            .catch(() => console.error)
            .finally(() => setKillAllSessions(false));
    }

    // eslint-disable-next-line react-hooks/rules-of-hooks
    useEffect(() => {
        getCsrfToken().then(token => {
            setCsrfToken(token)
        });
        getSessionList();
    }, []);

    return (
        <>
            <section className="profile-wrapper">
                <section className="main-block profile-info-wrapper">
                    <div className="profile-avatar">
                        {!user ? (
                            <Avatar icon={<User />} size={avatarSize}></Avatar>
                        ) : (
                            user.avatar ? (
                                <Avatar src={serverUrl + user.avatar} size={avatarSize}></Avatar>
                            ) : (
                                <Avatar size={avatarSize}>{user.username && (user.username[0])}</Avatar>
                            )
                        )}
                    </div>

                    <h1 className="profile-top-title">Мой профиль</h1>

                    <Form
                        form={form}
                        fields={[{ name: ['username'], value: user && user.username }, { name: ['user', 'email'], value: user && user.email }]}
                        variant={'filled'}
                    >
                        <Form.Item
                            name={'username'}
                            label="Логин"
                            rules={[{ required: true, message: 'Имя пользователя обязательно' }]}
                        >
                            <Input/>
                        </Form.Item>
                        <Form.Item
                            name={['user', 'email']}
                            label="E-mail"
                            rules={[
                                { required: true, message: "Введите email" },
                                { type: "email", message: "Невалидный email" },
                            ]}
                        >
                            <Input/>
                        </Form.Item>
                    </Form>

                    <Button color={'primary'} variant={'solid'}>Сохранить</Button>
                </section>

                <section className="main-block sessions-top-wrapper">
                    <h2 className="sessions-top-title">Мои активные сессии</h2>

                    <List
                        loading={{
                            spinning: sessionLoading,
                            indicator: <LoadingOutlined spin />,
                            size: "large"
                        }}
                        dataSource={sessionList}
                        renderItem={(session) => (
                            <List.Item
                                key={session.session_key}

                                actions={[
                                    !session.isCurrent ? [
                                        <Button
                                            key="block"
                                            onClick={() => handleBlockSession(session.session_key)}
                                            loading={blockSessionLoading}
                                        >
                                            Заблокировать
                                        </Button>,
                                        <Button
                                            key="end"
                                            onClick={() => handleEndSession(session.session_key)}
                                            loading={endSessionLoading} style={{ margin: '0 0 0 1rem' }}
                                        >
                                            Завершить
                                        </Button>
                                    ] : (
                                        <Link className="profile-logout" to="/user/logout">Выход</Link>
                                    )
                                ]}
                            >
                                <List.Item.Meta
                                    title={`Сессия: ${session.ip} ${session.isCurrent && "(Текущяя)"}`}
                                    description={`${session.os_info} Истекает: ${new Date(session.expire_date).toLocaleString()}`}
                                />
                            </List.Item>
                        )}
                    >
                    </List>

                    <Button onClick={handleKillAllSessions} disabled={sessionList.length <= 1} loading={killAllSessions} type={'primary'}>
                        Завершить другие
                    </Button>
                </section>
            </section>
        </>
    )
}

export default Profile;