import { serverUrl } from '../../Config.jsx'

import {Google, Logo} from "../../../icons/icons.jsx";
import {Button, Carousel, Form, Input, Space} from "antd";
import axios from "axios";

function Enter({ csrf, handleEnter }) {
    const [form] = Form.useForm();

    const onFinish = async (values) => {
        try {
            const formData = new FormData();
            formData.append("code", values.user.code);

            axios.post(serverUrl + "api/lr-enter-code/", formData, {
                withCredentials: true,
                headers: {'Content-Type': 'multipart/form-data', 'X-CSRFToken': csrf}
            })
                .then(res => {
                    handleEnter()
                })
                .catch(err => {
                    console.error(err);
                })
        } catch (error) {
            console.error("Ошибка соединения");
        }
    };

    return (
        <section className="lr-wrapper main-block">
            <section className="lr-form-wrapper">
                <div className="lr-form-top">
                    <Logo style={{ width: '25px', height: 'auto' }} />
                    <h1 className="lr-form-top-title">Добро пожаловать</h1>
                </div>

                <Form
                    form={form}
                    variant={'outlined'}
                    onFinish={onFinish}
                    layout="vertical"
                    initialValues={{ variant: 'filled' }}
                >
                    <Form.Item
                        name={['user', 'code']}
                        label="Код подтверждения"
                        rules={[
                            { required: true, message: "Введите код" },
                        ]}
                        hasFeedback
                        validateStatus="success"
                    >
                        <Input.OTP
                            formatter={(str) => str.replace(/\D/g, '')}
                            maxLength={6}
                            onChange={(value) => {if (value.length === 6) {form.submit()}}}
                        />
                    </Form.Item>

                    <Form.Item>
                        <Space>
                            <Button type="primary" htmlType="submit">Продолжить</Button>
                        </Space>
                    </Form.Item>
                </Form>
            </section>
        </section>
    )
}

export default Enter;