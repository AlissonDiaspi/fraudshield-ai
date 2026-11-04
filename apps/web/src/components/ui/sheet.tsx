"use client";

import * as React from "react";
import { Dialog } from "radix-ui";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

export const Sheet = Dialog.Root;
export const SheetTrigger = Dialog.Trigger;
export const SheetTitle = Dialog.Title;
export const SheetDescription = Dialog.Description;
export const SheetClose = Dialog.Close;
export function SheetContent({
  className,
  children,
  ...props
}: React.ComponentProps<typeof Dialog.Content>) {
  return (
    <Dialog.Portal>
      <Dialog.Overlay className="fixed inset-0 z-50 bg-black/65 backdrop-blur-sm" />
      <Dialog.Content
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-72 max-w-[90vw] flex-col border-r border-border bg-sidebar p-5 shadow-2xl outline-none",
          className,
        )}
        {...props}
      >
        {children}
        <Dialog.Close className="absolute right-3 top-3 rounded-lg p-2 text-muted-foreground hover:bg-accent focus-visible:ring-2 focus-visible:ring-ring">
          <X className="size-5" />
          <span className="sr-only">Fechar navegação</span>
        </Dialog.Close>
      </Dialog.Content>
    </Dialog.Portal>
  );
}
