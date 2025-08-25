import "./App.css";
import LoginPage from "./pages/LoginPage";
import { BrowserRouter } from "react-router";
import { ContextProvider } from "./context/ContextProvide";
function App() {
  return (
    <ContextProvider>
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
    </ContextProvider>
  );
}

export default App;
