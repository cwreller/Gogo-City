import { useEffect, RefObject } from 'react';

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: Record<string, unknown>) => void;
          renderButton: (element: HTMLElement, config: Record<string, unknown>) => void;
          prompt: () => void;
        };
      };
    };
  }
}

interface Options {
  buttonRef: RefObject<HTMLDivElement | null>;
  onCredential: (credential: string) => void;
  buttonConfig?: Record<string, unknown>;
}

/**
 * Initializes Google Identity Services once the GSI script has loaded and
 * renders the official Google button into `buttonRef`.
 *
 * The GSI script is loaded with `async` in index.html, so `window.google` may
 * not exist yet when a component mounts. We poll briefly until it appears,
 * then call `id.initialize` exactly once.
 */
export function useGoogleSignIn({ buttonRef, onCredential, buttonConfig }: Options) {
  useEffect(() => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
    if (!clientId) {
      console.warn('VITE_GOOGLE_CLIENT_ID is not set; Google sign-in disabled.');
      return;
    }

    let cancelled = false;
    let intervalId: number | undefined;

    const init = () => {
      if (cancelled || !window.google) return;

      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: (response: { credential: string }) => onCredential(response.credential),
      });

      if (buttonRef.current) {
        window.google.accounts.id.renderButton(buttonRef.current, {
          theme: 'filled_black',
          size: 'large',
          width: buttonRef.current.offsetWidth || 320,
          text: 'signin_with',
          ...buttonConfig,
        });
      }
    };

    if (window.google) {
      init();
    } else {
      intervalId = window.setInterval(() => {
        if (window.google) {
          window.clearInterval(intervalId);
          intervalId = undefined;
          init();
        }
      }, 100);
    }

    return () => {
      cancelled = true;
      if (intervalId !== undefined) window.clearInterval(intervalId);
    };
  }, [buttonRef, onCredential, buttonConfig]);
}

/**
 * Clicks the real (possibly hidden) Google button that GSI renders.
 * More reliable than `google.accounts.id.prompt()`, which Chrome rate-limits
 * and which is subject to FedCM restrictions.
 */
export function triggerGoogleSignIn(container: HTMLElement | null) {
  if (!container) return;
  const btn = container.querySelector<HTMLElement>('div[role="button"], button');
  if (btn) {
    btn.click();
  } else {
    window.google?.accounts.id.prompt();
  }
}
