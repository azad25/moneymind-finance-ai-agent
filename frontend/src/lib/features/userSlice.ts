import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UserState {
    isAuthenticated: boolean;
    user: {
        firstName: string;
        lastName: string;
        email: string;
    } | null;
}

const initialState: UserState = {
    isAuthenticated: false,
    user: null,
};

export const userSlice = createSlice({
    name: 'user',
    initialState,
    reducers: {
        login: (state, action: PayloadAction<{ firstName: string; lastName: string; email: string }>) => {
            state.isAuthenticated = true;
            state.user = action.payload;
        },
        logout: (state) => {
            state.isAuthenticated = false;
            state.user = null;
        },
        updateProfile: (state, action: PayloadAction<Partial<UserState['user']>>) => {
            if (state.user) {
                state.user = { ...state.user, ...action.payload };
            }
        },
    },
});

export const { login, logout, updateProfile } = userSlice.actions;
export default userSlice.reducer;
