"use client";

import { useState } from "react";

type FormState = "idle" | "submitting" | "success" | "error";

export default function IntakePage() {
  const [state, setState] = useState<FormState>("idle");
  const [error, setError] = useState<string>("");

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setState("submitting");
    setError("");

    const form = e.currentTarget;
    const data = {
      business_name: (form.elements.namedItem("business_name") as HTMLInputElement).value.trim(),
      client_email: (form.elements.namedItem("client_email") as HTMLInputElement).value.trim(),
      industry: (form.elements.namedItem("industry") as HTMLInputElement).value.trim(),
      budget_range: (form.elements.namedItem("budget_range") as HTMLSelectElement).value,
      urgency: (form.elements.namedItem("urgency") as HTMLSelectElement).value,
      description: (form.elements.namedItem("description") as HTMLTextAreaElement).value.trim(),
    };

    try {
      const res = await fetch("/api/intake", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      const json = await res.json();
      if (!res.ok) throw new Error(json.error || "Something went wrong");

      setState("success");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unexpected error");
      setState("error");
    }
  }

  if (state === "success") {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6" style={{colorScheme: "light"}}>
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-10 max-w-lg w-full text-center text-gray-900">
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">We got it — thank you.</h2>
          <p className="text-gray-500 text-sm">
            We received your information and are preparing a custom proposal. You'll hear from us shortly.
          </p>
          <a
            href="https://southpeak-systems.com"
            className="inline-flex items-center gap-1 text-sm text-gray-400 hover:text-gray-600 mt-6"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
            Back to SouthPeak Systems
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6" style={{colorScheme: "light"}}>
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-10 max-w-xl w-full text-gray-900">
        <div className="mb-8">
          <a
            href="https://southpeak-systems.com"
            className="inline-flex items-center gap-1 text-sm text-gray-400 hover:text-gray-600 mb-6"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
            Back to SouthPeak Systems
          </a>
          <h1 className="text-2xl font-semibold text-gray-900">Get a custom AI automation proposal</h1>
          <p className="text-gray-500 text-sm mt-1">
            Tell us what's slowing your team down. We'll send you a custom proposal with pricing — no sales call required.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Business name <span className="text-red-500">*</span>
              </label>
              <input
                name="business_name"
                type="text"
                required
                placeholder="Acme HVAC"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Your email <span className="text-red-500">*</span>
              </label>
              <input
                name="client_email"
                type="email"
                required
                placeholder="you@company.com"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Industry / type of business
            </label>
            <input
              name="industry"
              type="text"
              placeholder="e.g. HVAC, real estate, e-commerce"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Describe your project or problem <span className="text-red-500">*</span>
            </label>
            <textarea
              name="description"
              required
              rows={5}
              placeholder="What's taking up too much of your team's time? What would you like automated or built?"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 resize-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Budget range</label>
              <select
                name="budget_range"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 bg-white"
              >
                <option value="">Not sure yet</option>
                <option value="Under $2,000">Under $2,000</option>
                <option value="$2,000–$5,000">$2,000–$5,000</option>
                <option value="$5,000–$15,000">$5,000–$15,000</option>
                <option value="$15,000–$50,000">$15,000–$50,000</option>
                <option value="$50,000+">$50,000+</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Timeline</label>
              <select
                name="urgency"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 bg-white"
              >
                <option value="low">No rush — exploring options</option>
                <option value="medium">Within the next few months</option>
                <option value="high">As soon as possible</option>
              </select>
            </div>
          </div>

          {state === "error" && (
            <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <p className="text-xs text-gray-400 text-center">You'll hear back within 24 hours.</p>

          <button
            type="submit"
            disabled={state === "submitting"}
            className="w-full bg-gray-900 text-white text-sm font-medium py-2.5 rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {state === "submitting" ? "Preparing your proposal…" : "Submit"}
          </button>
        </form>
      </div>
    </div>
  );
}
