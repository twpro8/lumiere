import { createFileRoute } from "@tanstack/react-router"
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/_layout/")({
    component: () => (
        <div className="flex h-screen w-screen items-center justify-center flex-col gap-2">
            <p>Nothing here...</p>
            <Button>Click me!</Button>
        </div>
    ),
})
