"use client";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <h1 className="text-4xl font-bold mb-4">Find Your Perfect Makeup</h1>
      <p className="text-lg text-gray-600 text-center max-w-md mb-6">
        Answer a few questions and optionally upload an image to get personalized makeup recommendations.
      </p>
      <button
        onClick={() => router.push("/recommendation")}
        className="px-6 py-3 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600"
      >
        Get Started
      </button>
    </div>
  );
}
