import type { Transaction } from "../@types/transaction";
import type { Contractor } from "../@types/contractor";
import type { User } from "../@types/user";
export interface State {
  user: User | null;
  errors: string[];
  transactions: {
    isLoading: boolean;
    transactionsPagination: {
      transaction: Transaction[];
      pagination: {
        has_next: boolean;
        has_prev: boolean;
        page: number;
        pages: number;
        total: number;
        per_page: number;
      };
    };
    transaction: Transaction | null;
  };
  contractors: {
    isLoading: boolean;
    contractors: Contractor[];
  };
}
