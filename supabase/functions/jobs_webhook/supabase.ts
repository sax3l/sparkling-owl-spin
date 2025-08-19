import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (_req) => {
  // TODO: Implement Supabase client logic for webhooks.
  console.log("Supabase client for webhooks stub");

  const data = {
    message: "This is a stub function for jobs webhook supabase client.",
  };

  return new Response(
    JSON.stringify(data),
    { headers: { "Content-Type": "application/json" } },
  )
})