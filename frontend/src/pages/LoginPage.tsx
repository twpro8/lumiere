import { LoginForm } from "@/components/login-form"
import type { LoginRequest } from "@/schemas/auth.ts";

export function LoginPage() {
    return (
        <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
            <div className="w-full max-w-xs">
                <LoginForm
                    submit={((data: LoginRequest) => {
                        console.log(data)
                    })}
                    loading={false}
                    error={null}
                />
            </div>
        </div>
    )
}
