import { Context } from "./useContext";
import { useReducer } from "react";
import type { ReactNode } from "react";
import { taskReducer, initialState } from "./useContext";
export const ContextProvider = ({ children }: { children: ReactNode }) => {
  const [state, dispatch] = useReducer(taskReducer, initialState);

  return (
    <Context.Provider value={{ state, dispatch }}>{children}</Context.Provider>
  );
};
