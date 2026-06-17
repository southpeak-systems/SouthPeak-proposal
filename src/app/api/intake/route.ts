import { NextRequest, NextResponse } from "next/server";

export const maxDuration = 60; // seconds — upgrade to 300 on Pro if needed

export async function POST(req: NextRequest) {
  const body = await req.json();
  const { business_name, client_email, industry, budget_range, urgency, description } = body;

  if (!description || !client_email || !business_name) {
    return NextResponse.json(
      { error: "business_name, client_email, and description are required" },
      { status: 400 }
    );
  }

  const backendUrl = process.env.BACKEND_URL;
  if (!backendUrl) {
    return NextResponse.json({ error: "Backend not configured" }, { status: 500 });
  }

  const raw_input = [
    `Business: ${business_name}`,
    industry ? `Industry: ${industry}` : null,
    budget_range ? `Budget: ${budget_range}` : null,
    urgency ? `Timeline: ${urgency}` : null,
    ``,
    description,
  ]
    .filter(Boolean)
    .join("\n");

  const response = await fetch(`${backendUrl}/intake`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ raw_input, client_email, business_name }),
    signal: AbortSignal.timeout(120_000),
  });

  if (!response.ok) {
    const text = await response.text();
    return NextResponse.json({ error: text || "Backend error" }, { status: 502 });
  }

  const result = await response.json();
  // Never expose doc_url or internal IDs to the client browser
  return NextResponse.json({ success: true });
}
