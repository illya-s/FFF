import { serverUrl } from '../../Config.jsx'

import axios from "axios";

import {Google, Logo} from "../../../icons/icons.jsx";
import {Button, Form, Input } from "antd";

function Request({ csrf, handleSuccess }) {
    const [form] = Form.useForm();

    const onFinish = async (values) => {
        try {
            const formData = new FormData();
            formData.append("email", values.user.email);

            axios.post(serverUrl + "api/lr-request-code/", formData, {
                withCredentials: true,
                headers: {'Content-Type': 'multipart/form-data', 'X-CSRFToken': csrf}
            })
                .then(res => {
                    console.log(res.message)
                    handleSuccess()
                })
                .catch(err => {
                    console.error(err);
                })
        } catch (error) {
            console.error(`Ошибка соединения\n${error}`);
        }
    };

    return (
        <section className="lr-wrapper main-block">
            <section className="lr-form-wrapper">
                <div className="lr-form-top">
                    <Logo />
                    <h1 className="lr-form-top-title">Вход / Регистрация</h1>
                </div>

                <Form
                    form={form}
                    variant={'outlined'}
                    className="lr-form-inline"
                    onFinish={onFinish}
                    layout="vertical"
                    initialValues={{ variant: 'filled' }}
                >
                    <Form.Item
                        name={['user', 'email']}
                        label="Email"
                        rules={[
                            { required: true, message: "Введите email" },
                            { type: "email", message: "Невалидный email" },
                        ]}
                    >
                        <Input/>
                    </Form.Item>

                    <Form.Item>
                        <Button style={{ alignSelf: 'end' }} type="primary" htmlType="submit">Продолжить</Button>
                    </Form.Item>
                </Form>

                <div className="socialaccount-hr">
                    <hr/><h2>или</h2><hr/>
                </div>

                <div className="social-login-list">
                    <a className="social-login-btn social-login-{{ providers.0.id }}">
                        <Google style={{width:'25px',height:'max-content'}} />
                        Google
                    </a>
                </div>
            </section>
        </section>
    )
}


export default Request;