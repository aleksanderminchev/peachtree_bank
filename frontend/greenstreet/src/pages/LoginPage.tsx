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
            <TextField label="Username" type="text"></TextField>
            <TextField label="Password" type="password"></TextField>
            <Button onClick={() => {}}>Forgot password?</Button>
            </Stack>
          </CardContent>
          <CardActions>
            <Button onClick={() => {}}>Login</Button>
          </CardActions>
        </Card>
      </Box>
    </>
  );
}
