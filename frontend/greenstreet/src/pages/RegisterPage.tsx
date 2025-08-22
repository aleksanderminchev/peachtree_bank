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

export default function LoginPage() {
  return (
    <>
      <Box>
        <Card>
          <CardHeader>Login</CardHeader>
          <CardContent>
            <Stack direction={'column'} spacing={2}>
            <TextField label="Email" type="text"></TextField>

            <TextField label="Username" type="text"></TextField>
            <TextField label="Password" type="password"></TextField>
            <TextField label="Confirm password" type="password"></TextField>

            </Stack>
          </CardContent>
          <CardActions>
            <Button onClick={() => {}}>Register</Button>
          </CardActions>
        </Card>
      </Box>
    </>
  );
}
