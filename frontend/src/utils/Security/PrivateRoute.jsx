import React, { useContext } from "react";
import {   Navigate  } from "react-router-dom";

import { UserContext } from "./UserContext";

const PrivateRoute = (props) => {
    const { component: Component, path, componentProps, ...rest } = props;
    
    const { user_id, loading} = useContext(UserContext);
    
    if (!user_id && !loading) return <Navigate
        to={{
            pathname: "/",
        }}
    />

    return <Component {...props} {...componentProps} />
};

export default PrivateRoute;
