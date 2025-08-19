import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (_req) => {
  // TODO: Implement Supabase function for recomputing data quality metrics.
  console.log("DQ Recompute function stub");

  const data = {
    message: "This is a stub function for DQ Recompute.",
  };

  return new Response(
    JSON.stringify(data),
    { headers: { "Content-Type": "application/json" } },
  )
})