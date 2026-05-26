function ProfileCard({ title, children, className }) {
  return (
    <div
      className={`
        bg-white/5
        backdrop-blur-lg
        border
        border-white/10
        p-6
        rounded-3xl
        shadow-xl
        transition-all
        duration-300
        hover:border-white/20
        ${className || ""}
      `}
    >
      {title && <h2 className="text-xl font-bold mb-6 border-b border-white/5 pb-3">{title}</h2>}
      {children}
    </div>
  )
}

export default ProfileCard
