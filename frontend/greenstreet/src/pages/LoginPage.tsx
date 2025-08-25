import {
  Card,
  CardHeader,
  CardActions,
  CardContent,
  TextField,
  Button,
  Box,
  Stack,
} from "@mui/material";
import { useTasks } from "../context/useContext";
import axios, { setSession } from "../services/axios";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function LoginPage() {
  const { state } = useTasks();
  const { user } = state;
  console.log(user);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const login = async () => {
    console.log("response");

    const response = await axios.post(
      "/api/login",
      {
        password: password,
        username: username,
      },
      {
        withCredentials: true,
      }
    );
    if (response.status === 200) {
      console.log(response.data);
      setSession(response.data.access_token);
      navigate("/transactions");
    }
    console.log(response);
  };
  return (
    <>
      <Box>
        <Card>
          <CardHeader>Login</CardHeader>
          <CardContent>
            <Stack direction={"column"} spacing={2}>
              <TextField
                label="Username"
                type="text"
                value={username}
                onChange={(e) => {
                  setUsername(e.target.value);
                }}
              ></TextField>
              <TextField
                label="Password"
                type="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                }}
              ></TextField>
              <Button onClick={() => {}}>Forgot password?</Button>
            </Stack>
          </CardContent>
          <CardActions>
            <Button
              onClick={() => {
                login();
              }}
            >
              Login
            </Button>
          </CardActions>
        </Card>
      </Box>
    </>
  );
}
