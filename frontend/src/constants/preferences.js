export const INVESTOR_TYPES = [
  { value: 'HODLER', label: 'HODLer (long-term holder)' },
  { value: 'DAY_TRADER', label: 'Day Trader' },
  { value: 'SWING_TRADER', label: 'Swing Trader' },
  { value: 'BEGINNER', label: 'Just getting started' },
]

export const CONTENT_TYPES = [
  { value: 'NEWS', label: 'News' },
  { value: 'CHARTS', label: 'Charts & Prices' },
  { value: 'SOCIAL', label: 'Social Sentiment' },
  { value: 'FUN', label: 'Fun & Memes' },
]

export const ASSETS = [
  { value: 'BTC', label: 'Bitcoin (BTC)' },
  { value: 'ETH', label: 'Ethereum (ETH)' },
  { value: 'SOL', label: 'Solana (SOL)' },
  { value: 'ADA', label: 'Cardano (ADA)' },
  { value: 'DOT', label: 'Polkadot (DOT)' },
  { value: 'MATIC', label: 'Polygon (MATIC)' },
  { value: 'AVAX', label: 'Avalanche (AVAX)' },
  { value: 'LINK', label: 'Chainlink (LINK)' },
  { value: 'XRP', label: 'XRP' },
  { value: 'DOGE', label: 'Dogecoin (DOGE)' },
]

export function toggleValue(list, value) {
  return list.includes(value) ? list.filter((item) => item !== value) : [...list, value]
}
