import { UserContext } from "../../utils/Security/UserContext";
import { useContext } from "react";
import Button from "@mui/material/Button";
import { useNavigate } from "react-router-dom";
const Dashboard = () => {
  const navigate = useNavigate();
  const { user, setUser } = useContext(UserContext);
  const logout = () => {
    setUser(undefined);
    navigate("/");
  };
  return (
    <div>
      <h1>Dashboard</h1>
      Welcome to the dashboard {user}
      <Button onClick={logout} />
    </div>
  );
};

export default Dashboard;
