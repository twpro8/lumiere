import { createRouter, RouterProvider } from "@tanstack/react-router"
import { StrictMode } from "react"
import ReactDOM from "react-dom/client"

import "./styles/globals.css"
import { routeTree } from "./routeTree.gen"
import { ThemeProvider } from "@/providers/ThemeProvider.tsx";

const router = createRouter({ routeTree })
declare module "@tanstack/react-router" {
    interface Register {
        router: typeof router
    }
}

ReactDOM.createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <ThemeProvider>
            <RouterProvider router={router} />
        </ThemeProvider>
    </StrictMode>,
)
