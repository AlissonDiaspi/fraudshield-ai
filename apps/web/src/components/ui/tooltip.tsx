"use client";

import * as React from "react";
import { Tooltip as Primitive } from "radix-ui";

export function Tooltip({
  children,
  content,
}: {
  children: React.ReactNode;
  content: string;
}) {
  return (
    <Primitive.Root>
      <Primitive.Trigger asChild>{children}</Primitive.Trigger>
      <Primitive.Portal>
        <Primitive.Content
          sideOffset={6}
          className="z-50 max-w-64 rounded-lg border border-border bg-popover px-3 py-2 text-xs leading-relaxed text-foreground shadow-xl"
        >
          {content}
          <Primitive.Arrow className="fill-popover" />
        </Primitive.Content>
      </Primitive.Portal>
    </Primitive.Root>
  );
}
export const TooltipProvider = Primitive.Provider;
