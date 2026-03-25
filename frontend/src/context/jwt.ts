export interface JwtPayload {
  sub: string;
  username: string;
  display_name: string;
  email: string;
  is_admin: boolean;
}

export function jwtDecode(token: string): JwtPayload | null {
  try {
    const payload = token.split('.')[1];
    const decoded = JSON.parse(atob(payload));
    if (!decoded.sub) return null;
    return {
      sub: decoded.sub,
      username: decoded.username || '',
      display_name: decoded.display_name || '',
      email: decoded.email || '',
      is_admin: decoded.is_admin || false,
    };
  } catch {
    return null;
  }
}
