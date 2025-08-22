import "./App.css";
import LoginPage from "./pages/LoginPage";
import { BrowserRouter } from "react-router";
function App() {
  return (
    <BrowserRouter>
      <div
        style={{
          backgroundColor: "white",
          width: "calc(100vw - 10px)",
          height: "calc(100vh - 10px)",
        }}
      >
        <LoginPage></LoginPage>
      </div>
    </BrowserRouter>
  );
}

export default App;
