import type { Contractor } from "./contractor";
import type { Currency, Methods, Status } from "./enums";
export type Transaction = {
  amount: number;
  contractor: Contractor;
  contractor_id: number;
  created_at: Date;
  currency: Currency;
  method: Methods;
  payed_at: Date | null;
  received_at: Date | null;
  sent_at: Date | null;
  status: Status;
  tracking_id: string;
  uid: number;
  updated_at: Date;
};
