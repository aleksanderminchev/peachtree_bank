import {
  Card,
  CardHeader,
  CardActions,
  CardContent,
  TextField,
  Button,
  Box,
} from "@mui/material";

export default function TransactionPage() {
  return (
    <>
      <Box>
        <Card>
          <CardHeader>Login</CardHeader>
          <CardContent>
            <TextField label="Username" type="text"></TextField>
            <TextField label="Password" type="password"></TextField>
            <Button onClick={() => {}}>Forgot password?</Button>
          </CardContent>
          <CardActions>
            <Button onClick={() => {}}>Login</Button>
          </CardActions>
        </Card>
      </Box>
    </>
  );
}
