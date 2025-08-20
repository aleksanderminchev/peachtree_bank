import {
  Card,
  CardHeader,
  CardActions,
  CardContent,
  TextField,
  Button,
} from "@mui/material";

export default function TransactionForm() {
  return (
    <>
      <Card>
        <CardHeader>Send Transaction</CardHeader>
        <CardContent>
          <TextField label="From account" type="text"></TextField>
          <TextField label="To account" type="text"></TextField>
          <TextField label="Amount" type="number"></TextField>
        </CardContent>
        <CardActions>
          <Button onClick={()=>{
            
          }}>Send transaction</Button>
        </CardActions>
      </Card>
    </>
  );
}
