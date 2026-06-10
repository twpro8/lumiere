import { createFileRoute } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/")({
    component: () => <div className="flex h-screen w-screen items-center justify-center">Nothing here...</div>,
})
