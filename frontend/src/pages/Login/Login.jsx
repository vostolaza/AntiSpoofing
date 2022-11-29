import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormControl from "@mui/material/FormControl";
import FormLabel from "@mui/material/FormLabel";
import { useEffect, useRef, useState } from "react";
import Stack from "@mui/material/Stack";
import Button from "@mui/material/Button";
import Modal from "@mui/material/Modal";
import VideoCapture from "../../components/VideoCapture";
import { useNavigate } from "react-router-dom";
import login from "../../api/login";
const Login = () => {
  // Fields
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const disableContinue = useRef(true);
  const navigate = useNavigate();

  // Modal
  const [open, setOpen] = useState(false);
  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const loginUser = async (body) => {
    try {
      const response = await login(body);
      alert(`Login successful! ${response.data}`);
      navigate("/dashboard");
    } catch (e) {
      console.log(e);
      alert("Login failed");
    }
  };

  useEffect(() => {
    disableContinue.current = username.length === 0 || password.length === 0;
  }, [password, username]);

  const navToSignUp = () => {
    navigate("/signup");
  };

  return (
    <div className="d-flex justify-content-center">
      <Box
        component="form"
        sx={{
          "& .MuiTextField-root": { m: 1, width: "25ch" },
          width: "40%",
        }}
        noValidate
        autoComplete="off"
      >
        <h1>Login</h1>
        <div>
          <TextField
            required
            value={username}
            label="Username"
            onChange={(e) => setUsername(e.target.value)}
            defaultValue=""
          />
        </div>
        <div>
          <TextField
            label="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            autoComplete="current-password"
          />
        </div>
        <Modal
          open={open}
          onClose={handleClose}
          aria-labelledby="modal-modal-title"
          aria-describedby="modal-modal-description"
        >
          <VideoCapture
            videoCapAction={loginUser}
            videoCapActionBody={{ username, password }}
            labelName={`login-${username}`}
          />
        </Modal>
        <div>
          <div>
            <Stack direction="row" justifyContent="space-between">
              <Button onClick={navToSignUp} variant="contained">
                Sign Up
              </Button>
              <Button
                onClick={handleOpen}
                disabled={disableContinue.current}
                variant="contained"
              >
                Continue
              </Button>
            </Stack>
          </div>
        </div>
      </Box>
    </div>
  );
};

export default Login;
