import axios from 'axios';
import { APP_CONFIG } from '@/config/appConfig';

export const api = axios.create({ baseURL: APP_CONFIG.apiBaseUrl });
