import type { ReactNode } from "react";

type NotepadPanelProps = {
  title?: string;
  eyebrow?: string;
  children: ReactNode;
  className?: string;
};

export function NotepadPanel({
  title,
  eyebrow,
  children,
  className = "",
}: NotepadPanelProps) {
  return (
    <section className={`notepad-panel ${className}`}>
      {eyebrow ? <p className="note-eyebrow">{eyebrow}</p> : null}
      {title ? <h2 className="note-heading">{title}</h2> : null}
      {children}
    </section>
  );
}
