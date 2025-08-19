import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  console.log("Supabase client for webhooks stub");
  return new Response(
    JSON.stringify({
      message: "Supabase client for webhooks stub",
    }),
    { headers: { "Content-Type": "application/json" } },
  )
})