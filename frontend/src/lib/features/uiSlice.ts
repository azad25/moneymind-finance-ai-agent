import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UiState {
    isSidebarCollapsed: boolean;
}

const initialState: UiState = {
    isSidebarCollapsed: false,
};

export const uiSlice = createSlice({
    name: 'ui',
    initialState,
    reducers: {
        toggleSidebar: (state) => {
            state.isSidebarCollapsed = !state.isSidebarCollapsed;
        },
        setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
            state.isSidebarCollapsed = action.payload;
        },
    },
});

export const { toggleSidebar, setSidebarCollapsed } = uiSlice.actions;
export default uiSlice.reducer;
