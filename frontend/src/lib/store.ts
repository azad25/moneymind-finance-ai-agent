import { configureStore } from '@reduxjs/toolkit';
import userReducer from './features/userSlice';
import financeReducer from './features/financeSlice';
import chatReducer from './features/chatSlice';
import uiReducer from './features/uiSlice';

export const makeStore = () => {
    return configureStore({
        reducer: {
            user: userReducer,
            finance: financeReducer,
            chat: chatReducer,
            ui: uiReducer,
        },
        middleware: (getDefaultMiddleware) =>
            getDefaultMiddleware({
                serializableCheck: false, // Disable for Date objects in mock data
            }),
    });
};

export type AppStore = ReturnType<typeof makeStore>;
export type RootState = ReturnType<AppStore['getState']>;
export type AppDispatch = AppStore['dispatch'];
