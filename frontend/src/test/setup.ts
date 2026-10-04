// Setup commun des tests : lightweight-charts dessine sur un canvas, absent de
// jsdom. Il est remplace par un double qui enregistre les appels.
import { vi } from "vitest";

export const chart = {
  series: {
    setData: vi.fn(),
    createPriceLine: vi.fn((options: { title: string }) => options),
    removePriceLine: vi.fn(),
  },
  fitContent: vi.fn(),
  remove: vi.fn(),
};

vi.mock("lightweight-charts", () => ({
  LineStyle: { Dashed: 2 },
  createChart: vi.fn(() => ({
    addCandlestickSeries: () => chart.series,
    timeScale: () => ({ fitContent: chart.fitContent }),
    remove: chart.remove,
  })),
}));
