import axios from "axios";
import { API_BASE } from "./urls";

export const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true, // keep if you use cookies/sessions
  timeout: 10000,
});
