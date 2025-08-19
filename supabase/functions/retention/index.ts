import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

// TODO: Implement Supabase function to enforce data retention policies.
serve(async (_req) => {
  console.log("Retention function stub");
  const data = {
    message: "Retention function stub",
  }

  return new Response(
    JSON.stringify(data),
    { headers: { "Content-Type": "application/json" } },
  )
})