import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Message } from '@/lib/types';

interface ChatState {
    messages: Message[];
    isTyping: boolean;
}

const initialState: ChatState = {
    messages: [],
    isTyping: false,
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
        clearChat: (state) => {
            state.messages = [];
        },
    },
});

export const { addMessage, setTyping, clearChat } = chatSlice.actions;
export default chatSlice.reducer;
