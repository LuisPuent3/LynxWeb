import { JwtPayload } from 'jsonwebtoken';

declare module 'jsonwebtoken' {
  export interface JwtPayload {
    rol?: number;
    id?: number;
  }
}