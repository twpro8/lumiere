import { Controller, useForm } from "react-hook-form"
import { Link } from "@tanstack/react-router"
import { zodResolver } from "@hookform/resolvers/zod"
import { Button } from "@/components/ui/button"
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import {
    Field,
    FieldDescription,
    FieldError,
    FieldGroup,
    FieldLabel,
} from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import {
    type SignupFormData,
    signupFormSchema,
    type SignupRequest,
} from "@/schemas/auth"
import { ROUTES } from "@/routes"

interface SignupFormProps extends React.ComponentProps<typeof Card> {
    submit: (data: SignupRequest) => void
    loading: boolean
    error: string | null
}

export function SignupForm({
    submit,
    loading,
    error,
    ...props
}: SignupFormProps) {
    const form = useForm<SignupFormData>({
        resolver: zodResolver(signupFormSchema),
        defaultValues: {
            full_name: "",
            email: "",
            password: "",
            confirmPassword: "",
        },
    })

    const onSubmit = (data: SignupFormData) => {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const { confirmPassword: _confirmPassword, ...payload } = data
        submit(payload)
    }

    return (
        <Card {...props}>
            <CardHeader>
                <CardTitle>Create an account</CardTitle>
                <CardDescription>
                    Enter your information below to create your account
                </CardDescription>
            </CardHeader>
            <CardContent>
                <form onSubmit={form.handleSubmit(onSubmit)}>
                    <FieldGroup>
                        <Controller
                            name="full_name"
                            control={form.control}
                            render={({ field, fieldState }) => (
                                <Field data-invalid={fieldState.invalid}>
                                    <FieldLabel htmlFor={field.name}>Full Name</FieldLabel>
                                    <Input
                                        {...field}
                                        id={field.name}
                                        aria-invalid={fieldState.invalid}
                                        type="text"
                                        placeholder="John Doe"
                                        required
                                    />
                                    {fieldState.invalid && (
                                        <FieldError errors={[fieldState.error]} />
                                    )}
                                </Field>
                            )}
                        />
                        <Controller
                            name="email"
                            control={form.control}
                            render={({ field, fieldState }) => (
                                <Field data-invalid={fieldState.invalid}>
                                    <FieldLabel htmlFor={field.name}>Email</FieldLabel>
                                    <Input
                                        {...field}
                                        id={field.name}
                                        aria-invalid={fieldState.invalid}
                                        type="email"
                                        placeholder="m@example.com"
                                        required
                                    />
                                    <FieldDescription>
                                        We&apos;ll use this to contact you. We will not share your
                                        email with anyone else.
                                    </FieldDescription>
                                    {fieldState.invalid && (
                                        <FieldError errors={[fieldState.error]} />
                                    )}
                                </Field>
                            )}
                        />
                        <Controller
                            name="password"
                            control={form.control}
                            render={({ field, fieldState }) => (
                                <Field data-invalid={fieldState.invalid}>
                                    <FieldLabel htmlFor={field.name}>Password</FieldLabel>
                                    <Input
                                        {...field}
                                        id={field.name}
                                        aria-invalid={fieldState.invalid}
                                        type="password"
                                        required
                                    />
                                    <FieldDescription>
                                        Must be at least 8 characters long.
                                    </FieldDescription>
                                    {fieldState.invalid && (
                                        <FieldError errors={[fieldState.error]} />
                                    )}
                                </Field>
                            )}
                        />
                        <Controller
                            name="confirmPassword"
                            control={form.control}
                            render={({ field, fieldState }) => (
                                <Field data-invalid={fieldState.invalid}>
                                    <FieldLabel htmlFor={field.name}>Confirm Password</FieldLabel>
                                    <Input
                                        {...field}
                                        id={field.name}
                                        aria-invalid={fieldState.invalid}
                                        type="password"
                                        required
                                    />
                                    <FieldDescription>
                                        Please confirm your password.
                                    </FieldDescription>
                                    {fieldState.invalid && (
                                        <FieldError errors={[fieldState.error]} />
                                    )}
                                </Field>
                            )}
                        />
                        <Field>
                            {error && <FieldError errors={[{ message: error }]} />}
                            <Button type="submit">
                                {loading ? "Creating account..." : "Create Account"}
                            </Button>
                            <FieldDescription className="px-6 text-center">
                                Already have an account? <Link to={ROUTES.LOGIN}>Sign in</Link>
                            </FieldDescription>
                        </Field>
                    </FieldGroup>
                </form>
            </CardContent>
        </Card>
    )
}
