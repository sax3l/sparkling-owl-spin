import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  console.log("Retention policy definition stub");
  return new Response(
    JSON.stringify({
      message: "Retention policy definition stub",
    }),
    { headers: { "Content-Type": "application/json" } },
  )
})