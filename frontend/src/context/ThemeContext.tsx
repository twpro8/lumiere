import { createContext } from "react";

export type Theme = "latte" | "frappe" | "macchiato" | "mocha";

interface ThemeContextValue {
    theme: Theme;
    setTheme: (theme: Theme) => void;
}

export const ThemeContext = createContext<ThemeContextValue | null>(null);
