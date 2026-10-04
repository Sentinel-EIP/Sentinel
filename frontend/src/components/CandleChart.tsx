import {
  type IChartApi,
  type ISeriesApi,
  type IPriceLine,
  LineStyle,
  type UTCTimestamp,
  createChart,
} from "lightweight-charts";
import { useEffect, useRef } from "react";

import type { AiResult, Candle } from "../api/types";

// Couleurs lues dans les tokens du design system : aucun hexadecimal en dur,
// aucun rouge/vert reflexe sur les prix (--candle-up / --candle-down).
function token(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

interface Props {
  candles: Candle[];
  cone: AiResult | null;
}

export default function CandleChart({ candles, cone }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const chart = useRef<IChartApi | null>(null);
  const series = useRef<ISeriesApi<"Candlestick"> | null>(null);

  useEffect(() => {
    if (!container.current) return;
    const c = createChart(container.current, {
      autoSize: true,
      layout: { background: { color: token("--surface-raised") }, textColor: token("--text-secondary") },
      grid: { vertLines: { color: token("--grid-line") }, horzLines: { color: token("--grid-line") } },
      timeScale: { timeVisible: true, borderColor: token("--border-subtle") },
      rightPriceScale: { borderColor: token("--border-subtle") },
    });
    series.current = c.addCandlestickSeries({
      upColor: token("--candle-up"),
      downColor: token("--candle-down"),
      wickUpColor: token("--candle-up"),
      wickDownColor: token("--candle-down"),
      borderVisible: false,
    });
    chart.current = c;
    return () => {
      c.remove();
      chart.current = null;
      series.current = null;
    };
  }, []);

  useEffect(() => {
    series.current?.setData(
      candles.map((k) => ({
        time: (Date.parse(k.ts) / 1000) as UTCTimestamp,
        open: k.open,
        high: k.high,
        low: k.low,
        close: k.close,
      })),
    );
    chart.current?.timeScale().fitContent();
  }, [candles]);

  // Cone de volatilite : deux lignes horizontales, bornes de l'amplitude probable.
  useEffect(() => {
    const s = series.current;
    if (!s || !cone) return;
    const lines: IPriceLine[] = [
      ["upper", cone.value.upper],
      ["lower", cone.value.lower],
    ].map(([label, price]) =>
      s.createPriceLine({
        price: price as number,
        color: token("--accent"),
        lineStyle: LineStyle.Dashed,
        lineWidth: 1,
        axisLabelVisible: true,
        title: `cone ${label === "upper" ? "haut" : "bas"}`,
      }),
    );
    return () => lines.forEach((l) => s.removePriceLine(l));
  }, [cone]);

  return <div ref={container} data-testid="candle-chart" style={{ height: 420 }} />;
}
