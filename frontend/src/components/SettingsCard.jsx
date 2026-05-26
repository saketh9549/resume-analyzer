function SettingsCard({ title, description, children, className }) {
  return (
    <div
      className={`
        bg-white/5
        backdrop-blur-lg
        border
        border-white/10
        p-8
        rounded-3xl
        shadow-xl
        transition-all
        duration-300
        hover:border-white/20
        ${className || ""}
      `}
    >
      {title && (
        <div className="mb-6 border-b border-white/5 pb-3">
          <h2 className="text-2xl font-bold">{title}</h2>
          {description && <p className="text-sm text-gray-400 mt-1">{description}</p>}
        </div>
      )}
      {children}
    </div>
  )
}

export default SettingsCard
