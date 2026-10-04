// Formats d'affichage, locale francaise.
const price = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 2, minimumFractionDigits: 2 });
const percent = new Intl.NumberFormat("fr-FR", { style: "percent", maximumFractionDigits: 1 });
const date = new Intl.DateTimeFormat("fr-FR", { dateStyle: "short", timeStyle: "short" });

export const formatPrice = (v: number) => price.format(v);
export const formatPercent = (v: number | null) => (v === null ? "—" : percent.format(v));
export const formatDate = (iso: string) => date.format(new Date(iso));
