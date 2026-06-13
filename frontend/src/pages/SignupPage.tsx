import { SignupForm } from "@/components/signup-form"
import type { SignupRequest } from "@/schemas/auth.ts";

export function SignupPage() {
    return (
        <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
            <div className="w-full max-w-sm">
                <SignupForm
                    submit={(data: SignupRequest) => {
                        console.log(data)
                    }}
                    loading={false}
                    error={null}
                />
            </div>
        </div>
    )
}
