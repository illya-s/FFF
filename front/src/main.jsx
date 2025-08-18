import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import {ConfigProvider} from 'antd';
import {UserProvider} from "./User.jsx";

import { Alert } from 'antd';
import {MessageProvider} from "./MessageProvider.jsx";


createRoot(document.getElementById('root')).render(
    <ConfigProvider theme={{
        components: {
            Message: {
                contentBg: 'var(--bl3-color)',
                colorText: 'var(--txt-color)',
            },
            Button: {
                borderColorDisabled: 'transparent',
                defaultBorderColor: 'transparent',
                defaultHoverBorderColor: 'transparent',
                defaultActiveBorderColor: 'transparent',

                defaultBg: 'var(--bl2-color)',
                defaultColor: 'var(--txt-color)',
                defaultHoverColor: 'var(--tit-color)',
                defaultActiveColor: 'var(--tit-color)',
                defaultHoverBg: 'var(--bl3-color)',
                defaultActiveBg: 'var(--bl3-color)',

                colorBgContainerDisabled: 'var(--bl2-color)',
                colorTextDisabled: 'var(--txt-color)',

                colorPrimary: 'var(--bn-color)',
                colorPrimaryHover: 'var(--bn-active-color)',
                primaryColor: 'var(--bn-txt-color)',

                solidTextColor: 'var(--bn-txt-color)',

                colorError: 'var(--danger-color)',
                colorErrorHover: 'var(--danger-active-color)',
                errorColor: 'var(--bn-txt-color)',

                colorBgTextActive: 'var(--bn-txt-color)'
            },
            Input: {
                activeBg: 'var(--bl2-color)',
                hoverBg: 'var(--bl2-color)',
                colorBgContainer: 'var(--bl2-color)',

                colorBorder: 'var(--bl3-color)',
                activeBorderColor: 'var(--txt-color)',
                hoverBorderColor: 'var(--txt-color)',

                colorText: 'var(--txt-color)',
            },
            Select: {
                colorBorder: 'var(--bl3-color)',
                activeBorderColor: 'var(--txt-color)',
                hoverBorderColor: 'var(--txt-color)',

                activeOutlineColor: 'transparent',
                multipleItemBorderColor: 'transparent',
                multipleItemBorderColorDisabled: 'transparent',

                clearBg: 'var(--bl2-color)',
                selectorBg: 'var(--bl2-color)',
                colorBgElevated: 'var(--bl2-color)',
                multipleItemBg: 'var(--bl3-color)',

                optionActiveBg: 'var(--bl3-color)',
                optionSelectedBg: 'var(--bl3-color)',
                optionSelectedColor: 'var(--tit-color)',

                colorText: 'var(--txt-color)',
                colorTextPlaceholder: 'var(--txt-color)',
                colorTextQuaternary: 'var(--txt-color)',
            },
            Radio: {
                buttonBg: 'var(--bl2-color)',
                buttonColor: 'var(--txt-color)',

                colorBorder: 'transparent',
                colorPrimaryActive: 'var(--txt-color)',

                buttonSolidCheckedActiveBg: 'var(--bn-color)',
                buttonSolidCheckedBg: 'var(--bn-color)',
                buttonSolidCheckedHoverBg: 'var(--bn-color)',
                buttonSolidCheckedColor: 'var(--bn-txt-color)',
            },
            Dropdown: {
                colorBgElevated: 'var(--bl2-color)',
                colorText: 'var(--txt-color)',
                controlItemBgHover: 'var(--bl3-color)',
                colorSplit: 'var(--txt-color)',
            },
            Descriptions: {
                colorText: 'var(--tit-color)',
                labelColor: 'var(--txt-color)'
            },
            Rate: {
                starBg: 'var(--txt-color)',
                starColor: 'gold',
                starSize: 30
            },
            Form: {
                colorBorder: 'var(--txt-color)',
                colorError: 'var(--danger-color)',
                labelRequiredMarkColor: 'var(--danger-color)',
                colorPrimary: 'var(--bn-color)',
                colorSuccess: 'var(--success-color)',
                colorText: 'var(--tit-color)',
                colorTextDescription: 'var(--txt-color)',
                labelColor: 'var(--txt-color)',

                itemMarginBottom: 16,
            },
            Card: {
                actionsBg: 'transparent',
                colorBgContainer: 'transparent',

                colorBorderSecondary: 'transparent',

                fontSizeLG: '.8rem',
                fontSize: '.7rem',
                colorTextHeading: 'var(--tit-color)',
                colorTextDescription: 'var(--txt-color)',

                bodyPadding: '5px 0 0 0',
            },
            Badge: {
                colorBorderBg: 'transparent',
            },
            FloatButton: {
                colorBgElevated: 'var(--bn-color)',
                colorText: 'var(--bn-txt-color)',
            },
            Skeleton: {
                gradientFromColor: 'var(--bl3-color)',
                gradientToColor: 'var(--txt-color)',
            },
            Pagination: {
                colorPrimary: 'var(--tit-color)',
                colorPrimaryBorder: 'transparent',
                colorPrimaryHover: 'var(--tit-color)',

                itemBg: 'var(--bl2-color)',
                itemActiveBg: 'var(--bl3-color)',

                colorText: 'var(--txt-color)',
                colorBgTextHover: 'var(--bl3-color)',
                colorBorder: 'transparent',
            },
            List: {
                colorBorder: 'var(--txt-color)',
                colorText: 'var(--tit-color)',
                colorTextDescription: 'var(--txt-color)',

                colorSplit: 'var(--br-color)',
            },
            Spin: {
                colorPrimary: 'var(--bn-color)',
            },
            Typography: {
                colorTextHeading: 'var(--tit-color)',
                colorText: 'var(--txt-color)',
            },
        },
    }}>
        <UserProvider>
            <MessageProvider>
                <App />
            </MessageProvider>
        </UserProvider>
    </ConfigProvider>
)
