

import { createContext } from "react";

export const UserContext = createContext({
    user: null,
    setUser: null,
    loading: null,
    setLoading: null,
    account_id: null,
    user_id: null,
    user_phone_number: null,
    hashedPasshword: null,
    setHashedPassword: null
});