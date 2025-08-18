import React, { createContext, useContext } from "react";
import { message } from "antd";

const MessageContext = createContext(null);

export function MessageProvider({ children }) {
    const [messageApi, contextHolder] = message.useMessage();

    return (
        <MessageContext.Provider value={messageApi}>
            {contextHolder}
            {children}
        </MessageContext.Provider>
    );
}

export function useMessageApi() {
    return useContext(MessageContext);
}