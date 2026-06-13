import * as z from "zod"

const loginFormSchema = z.object({
    email: z.email().max(128, "Email must be at most 128 characters"),
    password: z
        .string()
        .min(6, "Password must be at least 6 characters")
        .max(128, "Password must be at most 128 characters"),
})

const signupSchema = loginFormSchema.extend({
    full_name: z
        .string()
        .min(2, "Full name must be at least 2 characters")
        .max(64, "Full name must be at most 64 characters"),
})

const signupFormSchema = signupSchema
    .extend({
        confirmPassword: z.string(),
    })
    .refine((data) => data.password === data.confirmPassword, {
        error: "Passwords do not match",
        path: ["confirmPassword"],
    })

type LoginRequest = z.infer<typeof loginFormSchema>
type SignupRequest = z.infer<typeof signupSchema>
type SignupFormData = z.infer<typeof signupFormSchema>

export { loginFormSchema, signupFormSchema, signupSchema }
export type { LoginRequest, SignupRequest, SignupFormData }
