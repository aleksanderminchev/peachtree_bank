/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { createContext, useContext } from "react";
import type { State } from "../@types/state";
export const initialState: State = {
  user: null,
  errors: [],
  transactions: {
    isLoading: false,
    transactionsPagination: {
      transaction: [],
      pagination: {
        has_next: false,
        has_prev: false,
        page: 0,
        pages: 0,
        total: 0,
        per_page: 25,
      },
    },
    transaction: null,
  },
  contractors: {
    isLoading: false,
    contractors: [],
  },
};

export type Action =
  | { type: "SET_USER"; payload: any }
  | { type: "ADD_ERROR"; payload: any }
  | { type: "CLEAR_ERRORS" }
  | { type: "SET_CONTRACTORS"; payload: any }
  | { type: "SET_TRANSACTION"; payload: any }
  | { type: "SET_TRANSACTIONS"; payload: any }
  | { type: "RESET" };

// Reducer function
export const taskReducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "SET_USER":
      return { ...state, user: action.payload };
    case "ADD_ERROR":
      return { ...state, errors: [...state.errors, action.payload] };
    case "CLEAR_ERRORS":
      return { ...state, errors: [] };
    case "SET_CONTRACTORS":
      return {
        ...state,
        contractors: { isLoading: false, contractors: action.payload },
      };
    case "SET_TRANSACTIONS":
      return {
        ...state,
        transactions: {
          ...state.transactions,
          transactionsPagination: action.payload,
        },
      };
    case "SET_TRANSACTION":
      return {
        ...state,
        transactions: { ...state.transactions, transaction: action.payload },
      };
    case "RESET":
      return initialState;
    default:
      return state;
  }
};

interface ContextType {
  state: State;
  dispatch: React.Dispatch<Action>;
}
export const Context = createContext<ContextType | undefined>(undefined);

export const useTasks = () => {
  const context = useContext(Context);
  if (!context) {
    throw new Error("useTasks must be used within a ContextProvider");
  }
  return context;
};
