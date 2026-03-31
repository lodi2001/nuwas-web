"use client";

import { useEffect } from "react";

declare global {
  interface Window {
    AOS?: {
      init: (options: { duration: number; once: boolean }) => void;
    };
  }
}

export default function AOSInit() {
  useEffect(() => {
    const initAOS = () => {
      if (window.AOS) {
        window.AOS.init({ duration: 1000, once: true });
      }
    };

    if (window.AOS) {
      initAOS();
    } else {
      // Wait for AOS script to load
      const interval = setInterval(() => {
        if (window.AOS) {
          initAOS();
          clearInterval(interval);
        }
      }, 100);
      return () => clearInterval(interval);
    }
  }, []);

  return null;
}
