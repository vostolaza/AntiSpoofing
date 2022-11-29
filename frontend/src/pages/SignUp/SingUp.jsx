import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormControl from "@mui/material/FormControl";
import FormLabel from "@mui/material/FormLabel";
import { useEffect, useRef, useState } from "react";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import { useNavigate } from "react-router-dom";
import Modal from "@mui/material/Modal";
import VideoCapture from "../../components/VideoCapture";
import signup from "../../api/singup";
const SignUp = () => {
  const [disableContinueButton, setDisableContinueButton] = useState(true);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [gender, setGender] = useState("");
  const usernameError = useRef(username.length < 3);
  const passwordError = useRef(password.length < 6);
  const emailError = useRef(!email.includes("@"));
  const genderError = useRef(gender === "");

  const navigate = useNavigate();

  useEffect(() => {
    usernameError.current = username.length < 3;
    passwordError.current = password.length < 6;
    emailError.current = !email.includes("@");
    genderError.current = gender === "";
    setDisableContinueButton(
      usernameError.current ||
        passwordError.current ||
        emailError.current ||
        genderError.current
    );
  }, [username, password, email, gender]);

  const handleGenderChange = (event) => {
    setGender(event.target.value);
  };
  const signUpUser = async (body) => {
    try {
      const response = await signup(body);
      alert(`Sign up successful! ${response.data}`);
      navigate("");
    } catch (e) {
      console.log(e);
    }
  };
  // Modal
  const [open, setOpen] = useState(false);
  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

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
        <h1>Sign Up!</h1>

        <div>
          <TextField
            required
            error={usernameError.current}
            label="Username"
            helperText={
              usernameError.current
                ? "Username must be at least 3 characters long"
                : ""
            }
            onChange={(e) => setUsername(e.target.value)}
            value={username}
          />
          <TextField
            label="Password"
            error={passwordError.current}
            onChange={(e) => setPassword(e.target.value)}
            helperText={
              passwordError.current
                ? "Password must be at least 6 characters long"
                : ""
            }
            type="password"
            autoComplete="current-password"
          />
        </div>
        <div>
          <TextField
            required
            label="Email"
            error={emailError.current}
            onChange={(e) => setEmail(e.target.value)}
            helperText={emailError.current ? "Email must be valid" : ""}
            defaultValue=""
          />
        </div>
        <div>
          <FormControl>
            <FormLabel id="demo-row-radio-buttons-group-label">
              Gender
            </FormLabel>
            <RadioGroup
              row
              aria-labelledby="demo-row-radio-buttons-group-label"
              name="row-radio-buttons-group"
              value={gender}
              onChange={handleGenderChange}
            >
              <FormControlLabel
                value="female"
                control={<Radio />}
                label="Female"
              />
              <FormControlLabel value="male" control={<Radio />} label="Male" />
              <FormControlLabel
                value="other"
                control={<Radio />}
                label="Other"
              />
            </RadioGroup>
          </FormControl>
        </div>
        <Modal
          open={open}
          onClose={handleClose}
          aria-labelledby="modal-modal-title"
          aria-describedby="modal-modal-description"
        >
          <VideoCapture
            videoCapAction={signUpUser}
            videoCapActionBody={{ username, password, email, gender }}
            labelName={`signup-${username}`}
          />
        </Modal>
        <div>
          <Stack direction="row" justifyContent="space-between">
            <Button onClick={() => navigate("/")} variant="contained">
              Go to Login
            </Button>
            <Button
              disabled={disableContinueButton}
              onClick={handleOpen}
              variant="contained"
            >
              Continue
            </Button>
          </Stack>
        </div>
      </Box>
    </div>
  );
};

export default SignUp;
