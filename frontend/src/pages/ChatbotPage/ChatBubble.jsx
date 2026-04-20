import React from "react";

export function ChatBubble({ role, text }) {
  const isBot = role === "bot";

  return (
    <div className={`flex w-full ${isBot ? "justify-start" : "justify-end"}`}>
      {isBot && (
        <div className="mr-2 mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#1d3461] text-xs text-[#2563eb]">
          ✚
        </div>
      )}
      <div
        className={`max-w-[72%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isBot
            ? "rounded-tl-sm bg-[#111111] text-[#f5f5f5]"
            : "rounded-tr-sm bg-[#1d3461] text-[#93c5fd]"
        }`}
      >
        {text}
      </div>
    </div>
  );
}

export function TypingBubble({ transcript }) {
  return (
    <div className="flex w-full justify-start">
      <div className="mr-2 mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#1d3461] text-xs text-[#2563eb]">
        ✚
      </div>
      <div className="max-w-[72%] rounded-2xl rounded-tl-sm bg-[#111111] px-4 py-3 text-sm text-[#6b7280]">
        {transcript ? (
          <span className="text-[#9ca3af]">{transcript}</span>
        ) : (
          <span className="flex gap-1">
            <span className="animate-bounce">·</span>
            <span className="animate-bounce" style={{ animationDelay: "0.15s" }}>·</span>
            <span className="animate-bounce" style={{ animationDelay: "0.3s" }}>·</span>
          </span>
        )}
      </div>
    </div>
  );
}
