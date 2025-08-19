import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  console.log("Erasure function stub");
  return new Response(
    JSON.stringify({
      message: "Erasure function stub",
    }),
    { headers: { "Content-Type": "application/json" } },
  )
})