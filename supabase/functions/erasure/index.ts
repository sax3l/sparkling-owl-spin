import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

// TODO: Implement Supabase function to handle data erasure requests.
serve(async (_req) => {
  console.log("Erasure function stub");
  const data = {
    message: "Erasure function stub",
  }

  return new Response(
    JSON.stringify(data),
    { headers: { "Content-Type": "application/json" } },
  )
})