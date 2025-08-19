import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (_req) => {
  // TODO: Implement Supabase function to handle data erasure requests.
  console.log("Erasure function stub");

  const data = {
    message: "This is a stub function for Erasure.",
  };

  return new Response(
    JSON.stringify(data),
    { headers: { "Content-Type": "application/json" } },
  )
})