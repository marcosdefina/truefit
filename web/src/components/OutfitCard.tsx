import type { OutfitItem } from '../store/useStore'
import ColourSwatch from './ColourSwatch'

interface Props {
  item: OutfitItem
}

export default function OutfitCard({ item }: Props) {
  const categoryLabel = item.category.charAt(0).toUpperCase() + item.category.slice(1)

  return (
    <div className="card flex flex-col">
      {/* Product image */}
      <div className="aspect-[3/4] bg-brand-50 relative overflow-hidden">
        <img
          src={item.image}
          alt={item.name}
          className="w-full h-full object-cover"
          onError={(e) => {
            // Fallback for broken images
            const target = e.target as HTMLImageElement
            target.style.display = 'none'
            target.parentElement!.innerHTML = `
              <div class="w-full h-full flex items-center justify-center bg-brand-100">
                <span class="text-4xl opacity-30">${
                  item.category === 'top' ? '👕' : item.category === 'bottom' ? '👖' : '👟'
                }</span>
              </div>
            `
          }}
        />
        {/* Category badge */}
        <span className="absolute top-3 left-3 bg-white/90 backdrop-blur-sm text-brand-700 text-xs font-semibold px-2.5 py-1 rounded-full">
          {categoryLabel}
        </span>
      </div>

      {/* Details */}
      <div className="p-4 flex flex-col gap-2 flex-1">
        <h3 className="font-semibold text-brand-800 leading-tight">{item.name}</h3>

        <div className="flex items-center justify-between">
          <ColourSwatch hex={item.colour} name={item.colour_name} size="sm" />
          <span className="text-xs bg-brand-100 text-brand-600 px-2 py-0.5 rounded-md font-medium">
            Size {item.size}
          </span>
        </div>

        <div className="mt-auto pt-3 flex items-center justify-between border-t border-brand-100">
          <span className="text-lg font-bold text-brand-800">€{Number(item.price).toFixed(2)}</span>
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs font-semibold text-brand-600 hover:text-brand-800 transition-colors"
          >
            View in shop →
          </a>
        </div>
      </div>
    </div>
  )
}
