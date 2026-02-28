interface Props {
  hex: string | null
  name?: string | null
  size?: 'sm' | 'md'
}

export default function ColourSwatch({ hex, name, size = 'md' }: Props) {
  if (!hex) return null

  const dim = size === 'sm' ? 'w-5 h-5' : 'w-7 h-7'

  return (
    <div className="flex items-center gap-2">
      <span
        className={`${dim} rounded-full border border-brand-200 shadow-inner inline-block`}
        style={{ backgroundColor: hex }}
        title={name ?? hex}
      />
      {name && <span className="text-xs text-brand-500">{name}</span>}
    </div>
  )
}
