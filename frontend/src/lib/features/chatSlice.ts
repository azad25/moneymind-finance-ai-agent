import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Message } from '@/lib/types';

interface ChatState {
    messages: Message[];
    isTyping: boolean;
    streamingMessage: string | null;
    sessionId: string | null;
}

const initialState: ChatState = {
    messages: [],
    isTyping: false,
    streamingMessage: null,
    sessionId: null,
};

export const chatSlice = createSlice({
    name: 'chat',
    initialState,
    reducers: {
        addMessage: (state, action: PayloadAction<Message>) => {
            state.messages.push(action.payload);
        },
        setTyping: (state, action: PayloadAction<boolean>) => {
            state.isTyping = action.payload;
        },
        setStreamingMessage: (state, action: PayloadAction<string | null>) => {
            state.streamingMessage = action.payload;
        },
        setSessionId: (state, action: PayloadAction<string | null>) => {
            state.sessionId = action.payload;
        },
        clearChat: (state) => {
            state.messages = [];
            state.streamingMessage = null;
        },
        updateLastMessage: (state, action: PayloadAction<string>) => {
            if (state.messages.length > 0) {
                const lastMessage = state.messages[state.messages.length - 1];
                if (lastMessage.role === 'assistant') {
                    lastMessage.content = action.payload;
                }
            }
        },
    },
});

export const {
    addMessage,
    setTyping,
    setStreamingMessage,
    setSessionId,
    clearChat,
    updateLastMessage,
} = chatSlice.actions;

export default chatSlice.reducer;
