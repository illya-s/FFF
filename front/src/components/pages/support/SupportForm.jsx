import React from 'react';
import { Form, Input, Select, Button, message } from 'antd';
import axios from 'axios';
import {serverUrl} from "../../Config.jsx";

const { Option } = Select;
const { TextArea } = Input;

const SupportForm = () => {
    const [form] = Form.useForm();

    const onFinish = async (values) => {
        try {
            await axios.post(`${serverUrl}api/support/`, values, {
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            message.success('Ваше обращение отправлено!');
            form.resetFields();
        } catch (error) {
            message.error('Ошибка при отправке, попробуйте снова.');
        }
    };

    return (
        <Form
            form={form}
            layout="vertical"
            onFinish={onFinish}
            className="main-block"
        >
            <Form.Item
                label="Имя"
                name="full_name"
                rules={[{ required: true, message: 'Введите ваше имя' }]}
            >
                <Input />
            </Form.Item>

            <Form.Item
                label="Email"
                name="email"
                rules={[
                    { required: true, message: 'Введите email' },
                    { type: 'email', message: 'Некорректный email' },
                ]}
            >
                <Input />
            </Form.Item>

            <Form.Item
                label="Тема обращения"
                name="subject"
                rules={[{ required: true, message: 'Выберите тему' }]}
            >
                <Select>
                    <Option value="general">Общие вопросы</Option>
                    <Option value="playback">Проблемы с воспроизведением видео</Option>
                    <Option value="error">Сообщить об ошибке</Option>
                    <Option value="partnership">Сотрудничество</Option>
                    <Option value="ads">Реклама на сайте</Option>
                    <Option value="copyright">Жалоба от правообладателя</Option>
                    <Option value="account">Проблемы с аккаунтом</Option>
                    <Option value="comment">Жалоба на комментарий</Option>
                    <Option value="other">Другое</Option>
                </Select>
            </Form.Item>

            <Form.Item
                label="Сообщение"
                name="message"
                rules={[{ required: true, message: 'Введите сообщение' }]}
            >
                <TextArea rows={5} />
            </Form.Item>

            <Form.Item>
                <Button type="primary" htmlType="submit">
                    Отправить
                </Button>
            </Form.Item>
        </Form>
    );
};

export default SupportForm;
